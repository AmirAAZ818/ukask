"""Ties retriever.py and generator.py together into the full query-time
pipeline: question -> embedding -> search -> retrieved chunks -> LLM -> answer.
This is what the FastAPI endpoint will call once the backend exists."""

from . import generator, retriever

RELEVANCE_THRESHOLD = 0.52

def answer_question(query, k=5, search_fn=None):
    search_fn = search_fn or retriever.search
    chunks = search_fn(query, k=k)
    top_similarity = (1 - chunks[0]["distance"]) if chunks else 0

    if top_similarity < RELEVANCE_THRESHOLD:
        return {"answer": generator.NOT_FOUND_MESSAGE, "sources": []}

    answer = generator.generate_answer(query, chunks)
    return {
        "answer": answer,
        "sources": [
            {
                "text": c["text"],
                "source_file": c["metadata"].get("source_file"),
                "page": c["metadata"].get("page"),
                "title": c["metadata"].get("title"),
                "article_numbers": c["metadata"].get("article_numbers"),
                "chunk_type": c["metadata"].get("chunk_type"),
                "similarity": 1 - c["distance"],
            }
            for c in chunks
        ],
    }