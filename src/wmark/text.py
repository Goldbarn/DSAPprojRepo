"""Shared word processing rules, documented in README.md."""

import difflib
import re
import unicodedata
from collections.abc import Iterator

WORD_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*")
APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "＇": "'"})


def preprocess(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(APOSTROPHES)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")


def normalize(word: str) -> str:
    return word.casefold()


def iter_word_matches(preprocessed: str) -> Iterator[re.Match[str]]:
    """Word matches over text that has already been through `preprocess`."""
    return WORD_RE.finditer(preprocessed)


def words(text: str) -> list[str]:
    return [normalize(m.group()) for m in iter_word_matches(preprocess(text))]


def changed_words(original: str, edited: str) -> int:
    """Word occurrences changed between two texts, from a diff of normalized word sequences.

    Each replace/insert/delete block counts as the larger of its two sides.
    """
    a, b = words(original), words(edited)
    ops = difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in ops if tag != "equal")
