"""BM25 (lexical/keyword) index built from the same chunk text already
sitting in ChromaDB, no re-embedding, no new model. Used alongside dense
search for hybrid retrieval: BM25 catches exact term matches that dense
embeddings can dilute across a blurry semantic neighborhood, e.g. حذف و اضافه.

Whitespace tokenization, not hazm's word_tokenize, faster and good enough here.
"""

from rank_bm25 import BM25Okapi

_index = None
_chunks = None  # (id, text, metadata) tuples, aligned with _index's row order


def _tokenize(text):
    return text.split()


def _build_index(collection):
    global _index, _chunks
    result = collection.get(include=["documents", "metadatas"])
    _chunks = list(zip(result["ids"], result["documents"], result["metadatas"]))
    tokenized_docs = [_tokenize(text) for _, text, _ in _chunks]
    _index = BM25Okapi(tokenized_docs)


def reset():
    """Call after re-ingesting, so the next search rebuilds against the new data."""
    global _index, _chunks
    _index, _chunks = None, None


def search(query, collection, k=5):
    if _index is None:
        _build_index(collection)

    scores = _index.get_scores(_tokenize(query))
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    return [
        {"text": _chunks[i][1], "metadata": _chunks[i][2], "bm25_score": float(scores[i])}
        for i in ranked_indices
    ]