"""Pulls raw text out of a PDF, page by page, using native text when available
and falling back to OCR (ocr.py) only for pages that turn out to be scans."""

import fitz
from tqdm import tqdm

from . import config, ocr, tables


def iter_pages(pdf_path):
    """Yields (page_number, text, was_ocr, table_markdowns) for every page."""
    doc = fitz.open(pdf_path)
    force_ocr = pdf_path.name in config.FORCE_OCR_FILES
    pbar = tqdm(enumerate(doc, start=1), total=doc.page_count, desc=pdf_path.name, unit="page")
    for i, page in pbar:
        native_text = page.get_text().strip()
        if not force_ocr and len(native_text) >= config.NATIVE_TEXT_MIN_CHARS:
            pbar.set_postfix_str("native")
            page_tables = tables.extract_tables(page)
            yield i, native_text, False, page_tables
        else:
            pbar.set_postfix_str("OCR, slower")
            text = ocr.ocr_page(page).strip()
            yield i, text, True, []  # table detection needs gridlines, scans don't have any
    doc.close()


def extract_pdf(pdf_path):
    """Returns a list of {page, text, was_ocr, tables} dicts for the whole document."""
    return [
        {"page": page_num, "text": text, "was_ocr": was_ocr, "tables": page_tables}
        for page_num, text, was_ocr, page_tables in iter_pages(pdf_path)
    ]