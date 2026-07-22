"""Persists chunks and their embeddings in ChromaDB. Embeddings are supplied
directly (via embed.py) rather than through Chroma's built-in embedding_function."""

import chromadb

from . import config


def get_client():
    return chromadb.PersistentClient(path=str(config.CHROMA_DIR))


def reset_collection(client):
    """Drops and recreates the collection, so re-running ingestion never duplicates data."""
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet, nothing to drop
    
    return client.create_collection(
        config.COLLECTION_NAME,
        embedding_function=None,
        # our embeddings are normalized (embed.py uses normalize_embeddings=True),
        # chroma defaults to L2 otherwise, which isn't the metric bge-m3 was built for
        configuration={"hnsw": {"space": "cosine"}},
    )


def add_chunks(collection, chunks, embeddings, source_filename):
    ids = [f"{source_filename}::{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source_file": source_filename,
            "title": c["title"] or source_filename,
            "page": c["page"],
            # chroma metadata can't store lists, so join them, split(",") to get the list back
            "article_numbers": ",".join(c["article_numbers"]) if c["article_numbers"] else "unknown",
            "publication_date": c["publication_date"] or "unknown",
            "chunk_type": c.get("chunk_type", "text"),
        }
        for c in chunks
    ]
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)