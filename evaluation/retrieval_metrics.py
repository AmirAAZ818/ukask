"""Retrieval-only evaluation metrics. Free to run, pure local vector search,
no generation calls, so this is the one safe to run repeatedly while tuning.

Relevance is judged by matching the ground truth's article number (source
field, like 'ماده ۲۶') against each chunk's article_numbers metadata, the
same field built during chunking. Not a perfect proxy (the same article can
legitimately appear in more than one document), but good enough without
manual relevance labeling, and it's what we have.
"""

import re

from pipeline import normalize


def parse_article_number(source_field):
    """'ماده ۲۶' -> '26'. Returns None if no digits found."""
    digits = normalize.to_ascii_digits(source_field)
    match = re.search(r"\d+", digits)
    return match.group() if match else None


def _is_relevant(chunk, target_article):
    articles = chunk["metadata"].get("article_numbers", "")
    if not articles or articles == "unknown":
        return False
    return target_article in articles.split(",")


def hit_rate_at_k(retrieved, target_article, k):
    return 1.0 if any(_is_relevant(c, target_article) for c in retrieved[:k]) else 0.0


def reciprocal_rank(retrieved, target_article):
    for i, c in enumerate(retrieved, start=1):
        if _is_relevant(c, target_article):
            return 1.0 / i
    return 0.0


def precision_at_k(retrieved, target_article, k):
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for c in top_k if _is_relevant(c, target_article))
    return hits / len(top_k)


def average_precision(retrieved, target_article, total_relevant):
    """total_relevant is the count of matching chunks in the WHOLE collection,
    not just what got retrieved, that's what makes this different from precision_at_k."""
    if total_relevant == 0:
        return 0.0
    hits = 0
    sum_precisions = 0.0
    for i, c in enumerate(retrieved, start=1):
        if _is_relevant(c, target_article):
            hits += 1
            sum_precisions += hits / i
    return sum_precisions / total_relevant


def count_total_relevant(collection, target_article):
    """Scans the whole collection once. Fine to do per-question for a corpus
    this size, everything here is local, no API cost either way."""
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    count = 0
    for meta in all_meta:
        articles = meta.get("article_numbers", "")
        if articles and articles != "unknown" and target_article in articles.split(","):
            count += 1
    return count


def evaluate_retrieval(questions, k=5, search_fn=None):
    """search_fn: defaults to backend.retriever.search (dense-only), pass
    backend.retriever.search_hybrid instead to evaluate hybrid retrieval
    with the exact same metrics, for a direct comparison."""
    from backend import retriever
    from pipeline import config, store

    search_fn = search_fn or retriever.search

    client = store.get_client()
    collection = client.get_collection(config.COLLECTION_NAME)

    rows = []
    for item in questions:
        target = parse_article_number(item["source"])
        retrieved = search_fn(item["question"], k=k) if target else []
        total_relevant = count_total_relevant(collection, target) if target else 0

        rows.append({
            "id": item["id"],
            "question": item["question"],
            "source": item["source"],
            "target_article": target,
            "question_type": item["question_type"],
            "difficulty": item.get("difficulty"),
            "k": k,
            "hit_rate": hit_rate_at_k(retrieved, target, k) if target else None,
            "reciprocal_rank": reciprocal_rank(retrieved, target) if target else None,
            "precision_at_k": precision_at_k(retrieved, target, k) if target else None,
            "average_precision": average_precision(retrieved, target, total_relevant) if target else None,
            "retrieved": retrieved,  # kept for inspecting failures, not needed for the metrics themselves
        })
    return rows