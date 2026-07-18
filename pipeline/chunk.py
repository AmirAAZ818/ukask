"""Splits a document's normalized text into token-sized chunks and attaches
per-chunk metadata (page number, article number so far).

Needs internet access the first time it runs, since it downloads the tokenizer
that matches the embedding model.
"""

import re

from transformers import AutoTokenizer

from . import config

_tokenizer = None
# _ARTICLE_RE = re.compile(r"ماده\s+(\d+)\s*[.;,:]+")
_ARTICLE_RE = re.compile(r"م\s*ا\s*د\s*ه\s+(\d+)\s*[.;,:)]+")


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        print("    loading tokenizer (downloads once, cached after)...")
        _tokenizer = AutoTokenizer.from_pretrained(config.EMBEDDING_MODEL, token=config.HF_TOKEN)
        # we tokenize whole documents here just to get offsets for chunking,
        _tokenizer.model_max_length = int(1e9)
        print("    tokenizer ready")
    return _tokenizer


def find_article_numbers(text):
    """All 'ماده N' matches in the text, in order of first appearance, no duplicates."""
    seen = []
    for m in _ARTICLE_RE.findall(text):
        if m not in seen:
            seen.append(m)
    return seen


def _build_full_text(pages):
    """Joins normalized page texts into one string, remembering which char
    offset each page starts at so chunks can be mapped back to a page number."""
    full_text = ""
    page_starts = []  # (char_offset, page_number)
    for p in pages:
        page_starts.append((len(full_text), p["page"]))
        full_text += p["text"] + "\n\n"
    return full_text, page_starts


def _page_for_offset(offset, page_starts):
    page_num = page_starts[0][1]
    for start, num in page_starts:
        if start <= offset:
            page_num = num
        else:
            break
    return page_num


def chunk_document(pages, doc_meta):
    """pages: list of {page, text} already run through normalize.clean_text.
    doc_meta: {title, publication_date}.
    Returns a list of chunk dicts ready to embed and store."""
    tokenizer = _get_tokenizer()
    full_text, page_starts = _build_full_text(pages)

    encoding = tokenizer(full_text, return_offsets_mapping=True, add_special_tokens=False)
    offsets = encoding["offset_mapping"]

    step = config.MAX_CHUNK_TOKENS - config.CHUNK_OVERLAP_TOKENS
    chunks = []
    current_article = None  # last article number seen, carried into chunks with no marker of their own

    for start_tok in range(0, len(offsets), step):
        end_tok = min(start_tok + config.MAX_CHUNK_TOKENS, len(offsets))
        if end_tok - start_tok < config.MIN_CHUNK_TOKENS and chunks:
            break  # trailing sliver smaller than the min, fold it into the previous chunk instead

        char_start = offsets[start_tok][0]
        char_end = offsets[end_tok - 1][1]
        chunk_text = full_text[char_start:char_end].strip()
        if not chunk_text:
            continue

        found = find_article_numbers(chunk_text)
        if found:
            # the chunk may still open under the previous article, before its
            # first new "ماده" marker shows up
            article_numbers = ([current_article] if current_article and current_article not in found else []) + found
            current_article = found[-1]
        else:
            article_numbers = [current_article] if current_article else []

        chunks.append({
            "text": chunk_text,
            "page": _page_for_offset(char_start, page_starts),
            "article_numbers": article_numbers,
            "title": doc_meta.get("title"),
            "publication_date": doc_meta.get("publication_date"),
            "chunk_type": "text",
        })

        if end_tok == len(offsets):
            break

    return chunks