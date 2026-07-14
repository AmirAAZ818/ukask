"""Ties retriever.py and generator.py together into the full query-time
pipeline: question -> embedding -> search -> retrieved chunks -> LLM -> answer.
This is what the FastAPI endpoint will call once the backend exists."""

from . import generator, retriever


def answer_question(query, k=5):
    chunks = retriever.search(query, k=k)
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
                "similarity": 1 - c["distance"],  # chroma gives distance, UI wants similarity
            }
            for c in chunks
        ],
    }