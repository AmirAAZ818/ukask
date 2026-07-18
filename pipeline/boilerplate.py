"""Detects and strips repeating boilerplate lines (running headers/footers)
that show up on most pages of a document. Works by finding lines that recur across a large fraction of pages,
digits get normalized out first so a page number difference (32 vs 33)
doesn't prevent two otherwise-identical header lines from matching."""

import re
from collections import Counter

# regulatory content markers, never strip these regardless of how often they
# recur, "ماده 11" on its own line looks repetitive across many pages of a
# regulations document, but it's real content (which article is starting),
# not decoration
_PROTECTED_PREFIXES = ("ماده", "تبصره", "بند")


def _normalize_line(line):
    return re.sub(r"\d+", "#", line.strip())


def find_boilerplate_lines(pages_text, min_fraction=0.8, max_words=12, min_pages=3):
    """pages_text: list of raw page text strings, one per page, whole document.
    Returns the set of normalized line patterns appearing on at least
    min_fraction of pages, candidates for stripping.

    min_fraction defaults high on purpose, a genuine running header shows up
    on nearly every page, not just half of them, a lower threshold risks
    catching formulaic-but-real content instead (see _PROTECTED_PREFIXES).

    max_words caps how long a candidate line can be, real headers/footers
    are short, a long paragraph should never qualify even if it happens to
    follow a formulaic pattern.

    min_pages guards against a real edge case, with too few pages, any line
    trivially 'recurs' across a large fraction of them (on a 1-page document,
    every single line is technically on '100% of pages'). Below this many
    pages, detection is meaningless, so it's skipped entirely."""
    total_pages = len(pages_text)
    if total_pages < min_pages:
        return set()

    line_page_counts = Counter()
    for text in pages_text:
        lines_on_this_page = {
            _normalize_line(l) for l in text.split("\n")
            if l.strip()
            and len(l.strip().split()) <= max_words
            and not l.strip().startswith(_PROTECTED_PREFIXES)
        }
        for line in lines_on_this_page:
            line_page_counts[line] += 1

    return {
        line for line, count in line_page_counts.items()
        if line and count / total_pages >= min_fraction
    }


def strip_boilerplate(text, boilerplate_patterns):
    kept_lines = [l for l in text.split("\n") if _normalize_line(l) not in boilerplate_patterns]
    return "\n".join(kept_lines)