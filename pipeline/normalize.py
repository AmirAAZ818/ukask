"""Cleanup pass applied to text from both native extraction and OCR."""

import re

from hazm import Normalizer

_normalizer = Normalizer()

# maps Persian and Arabic-Indic digits to plain ASCII, needed since PDFs and
# OCR output mix all three digit systems and regex matching needs one form
_DIGIT_MAP = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹" "٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def to_ascii_digits(text):
    return text.translate(_DIGIT_MAP)


def clean_text(text):
    text = _normalizer.normalize(text)
    text = to_ascii_digits(text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # PDF line wraps mid-sentence -> join them
    text = re.sub(r"[ \t]+", " ", text)           # collapse repeated spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)        # collapse big vertical gaps
    return text.strip()


def clean_table_text(text):
    """Same character-level cleanup as clean_text, but skips the line-joining
    and whitespace collapsing, which destroy a markdown table's rows."""
    text = _normalizer.normalize(text)
    return to_ascii_digits(text).strip()