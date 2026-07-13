"""Detects tables on a native-text page and converts each to markdown, so the
row/column structure survives instead of collapsing into flattened text.

Only useful on native-text pages, table detection relies on vector gridlines,
so this isn't called for OCR pages."""


def extract_tables(page):
    """Returns a list of markdown strings, one per table found on the page."""
    found = page.find_tables()
    return [tab.to_markdown() for tab in found.tables]