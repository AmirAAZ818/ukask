"""Detects tables on a native-text page and converts each to markdown, so the
row/column structure survives instead of collapsing into flattened text.

Only useful on native-text pages, table detection relies on vector gridlines
or aligned text positions, scanned pages have neither (just a raster image),
so this isn't called for OCR pages, their tables just stay as flattened OCR
text for now."""


def extract_tables(page):
    """Returns a list of markdown strings, one per table found on the page.
    Tries gridline-based detection first, it's the more precise of the two.
    Only falls back to text-position detection (catches borderless tables,
    but is more prone to false positives) if the first pass found nothing."""
    found = page.find_tables()
    return [tab.to_markdown() for tab in found.tables]