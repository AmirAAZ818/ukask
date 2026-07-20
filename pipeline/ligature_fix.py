"""Fixes a font bug in some documents (B Zar and relatives) where the ل+ا
(lam-alef) sequence gets drawn in reversed order during extraction, turning
صحیح "لا" into "ال". Opt-in per file via config.LIGATURE_FIX_FILES, since a
corrupted "لا" and a genuinely correct "ال" (as in سال, مال, حال) are
identical once extracted, there's no telling them apart without outside
information, here that's word frequency.

Conservative by design: only swaps when the swapped reading is both common
and clearly more common than the as-extracted one. Ambiguous words are left
untouched rather than guessed at.
"""

import re

from hazm.utils import words_list

MIN_FREQ = 1000
MIN_RATIO = 10

_WORD_FREQ = None
_PUNCT_RE = re.compile(r'^([\u060C.,:;!?)\]}»"\'\u200c]*)(.*?)([\u060C.,:;!?(\[{«"\'\u200c]*)$')


def _get_word_freq():
    global _WORD_FREQ
    if _WORD_FREQ is None:
        _WORD_FREQ = {w: f for w, f, tags in words_list()}
    return _WORD_FREQ


def _fix_word(word, freq):
    match = _PUNCT_RE.match(word)
    prefix, core, suffix = match.groups() if match else ("", word, "")

    idx = core.find("ال")
    if idx == -1:
        return word

    swapped_core = core[:idx] + "لا" + core[idx + 2:]
    orig_freq = freq.get(core, 0)
    swapped_freq = freq.get(swapped_core, 0)
    if swapped_freq >= MIN_FREQ and swapped_freq >= orig_freq * MIN_RATIO:
        return prefix + swapped_core + suffix
    return word


def fix_text(text):
    freq = _get_word_freq()
    return " ".join(_fix_word(w, freq) for w in text.split(" "))