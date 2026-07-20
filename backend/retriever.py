"""Query-time retrieval, the part of the pipeline that runs on every request
rather than once offline. Embeds the incoming question and searches the
ChromaDB collection that pipeline.build_index already built."""

from pipeline import config, embed, store


def search(query, k=5):
    """Returns the top-k chunks for a query, each with its text, metadata,
    and distance (cosine distance, lower means more similar)."""
    client = store.get_client()
    collection = client.get_collection(config.COLLECTION_NAME)

    query_vector = embed.embed_texts([query])
    results = collection.query(query_embeddings=query_vector, n_results=k)

    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]


def _reciprocal_rank_fusion(ranked_lists, rrf_k=60):
    """score(chunk) = sum(1 / (rrf_k + rank)) across every list it appears in.
    rrf_k=60 is the standard constant from the original RRF paper, this is a
    field convention, not something that typically needs tuning. Chunks are
    matched across lists by their text, reliably unique within one collection."""
    scores = {}
    chunk_lookup = {}
    for ranked in ranked_lists:
        for rank, chunk in enumerate(ranked, start=1):
            key = chunk["text"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)
            chunk_lookup.setdefault(key, chunk)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True), chunk_lookup


def search_hybrid(query, k=5, candidate_k=20):
    """Combines dense search with BM25 keyword search via Reciprocal Rank
    Fusion. Returns the same shape as search() (text, metadata, distance),
    a drop-in replacement anywhere search() is used, including evaluation.

    'distance' is the real dense cosine distance when dense search found the
    chunk, keeping the relevance gate meaningful. For a BM25-only chunk, there
    is no real distance, so it gets the worst distance in the dense pool as a
    conservative stand-in."""
    from . import bm25_index

    client = store.get_client()
    collection = client.get_collection(config.COLLECTION_NAME)

    dense_results = search(query, k=candidate_k)
    bm25_results = bm25_index.search(query, collection, k=candidate_k)

    dense_distance_by_text = {c["text"]: c["distance"] for c in dense_results}
    worst_dense_distance = max(dense_distance_by_text.values(), default=1.0)

    ranked, chunk_lookup = _reciprocal_rank_fusion([dense_results, bm25_results])

    results = []
    for key, _ in ranked[:k]:
        chunk = chunk_lookup[key]
        results.append({
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "distance": dense_distance_by_text.get(key, worst_dense_distance),
        })
    return results