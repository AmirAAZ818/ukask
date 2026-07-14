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