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

# some documents extract a stray period where a می/نمی prefix should join
# directly to its verb (می‌شود -> "می . شود"). Not ambiguous like the لا/ال
# swap, no real Persian sentence ends on "می." and starts fresh with a verb,
# so this is safe to fix everywhere rather than gating it per file.
_VERB_JOIN_RE = re.compile(r"(\bن?می)[\s\u200c]*\.[\s\u200c]*(?=\S)")


def to_ascii_digits(text):
    return text.translate(_DIGIT_MAP)


def clean_text(text):
    text = _normalizer.normalize(text)
    text = to_ascii_digits(text)
    text = _VERB_JOIN_RE.sub("\\1\u200c", text)   # می . شود -> می‌شود
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # PDF line wraps mid-sentence -> join them
    text = re.sub(r"[ \t]+", " ", text)           # collapse repeated spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)        # collapse big vertical gaps
    return text.strip()


def clean_table_text(text):
    """Same character-level cleanup as clean_text, but skips the line-joining
    and whitespace collapsing, those would destroy a markdown table's rows."""
    text = _normalizer.normalize(text)
    return to_ascii_digits(text).strip()