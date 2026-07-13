"""One-time (re-run-whenever-the-PDFs-change) ingestion script.

    python -m pipeline.build_index

Rebuilds the whole ChromaDB collection from scratch every time it runs, on
purpose, so tweaking chunking or normalization never leaves stale chunks
behind from a previous version.
"""

from . import chunk, config, embed, extract, normalize, store


def _table_chunks(raw_pages, doc_meta):
    chunks = []
    for p in raw_pages:
        for md in p["tables"]:
            chunks.append({
                "text": normalize.clean_table_text(md),
                "page": p["page"],
                "article_numbers": [],  # tables aren't tracked against article state, known limitation
                "title": doc_meta.get("title"),
                "publication_date": doc_meta.get("publication_date"),
                "chunk_type": "table",
            })
    return chunks


def process_pdf(pdf_path):
    doc_meta = config.DOCUMENT_MANIFEST.get(pdf_path.name, {})
    raw_pages = extract.extract_pdf(pdf_path)
    pages = [{"page": p["page"], "text": normalize.clean_text(p["text"])} for p in raw_pages]

    ocr_pages = [p["page"] for p in raw_pages if p["was_ocr"]]
    if ocr_pages:
        print(f"    OCR used on page(s) {ocr_pages}")

    table_chunks = _table_chunks(raw_pages, doc_meta)
    if table_chunks:
        table_pages = sorted({c["page"] for c in table_chunks})
        print(f"    {len(table_chunks)} table(s) found on page(s) {table_pages}")

    text_chunks = chunk.chunk_document(pages, doc_meta)
    return text_chunks + table_chunks


def main():
    client = store.get_client()
    collection = store.reset_collection(client)

    pdf_paths = sorted(config.PDF_DIR.glob("*.pdf"))
    if not pdf_paths:
        print(f"No PDFs found in {config.PDF_DIR}, drop your regulation files there first.")
        return

    total_chunks = 0
    for pdf_path in pdf_paths:
        print(f"[{pdf_path.name}]")
        chunks = process_pdf(pdf_path)
        embeddings = embed.embed_texts([c["text"] for c in chunks])
        store.add_chunks(collection, chunks, embeddings, pdf_path.name)
        print(f"    {len(chunks)} chunks stored")
        total_chunks += len(chunks)

    print(f"\nDone. {total_chunks} chunks across {len(pdf_paths)} document(s) in '{config.COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()