import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from wmark.color import GREEN, word_color
from wmark.text import iter_word_matches, normalize, preprocess, words

# "he had a dog" must not become "he'd a dog".
MAIN_VERB_OBJECTS = {"a", "an", "the", "no", "to", "his", "her", "my", "your", "our", "their", "some", "any", "this", "that"}


@dataclass
class Substitution:
    position: int
    old: str
    new: str


@dataclass
class WatermarkResult:
    text: str
    initial_fraction: float
    final_fraction: float
    reached_target: bool
    stop_reason: str
    elapsed_seconds: float
    substitutions: list[Substitution] = field(default_factory=list)


def load_synonyms(path: Path) -> dict[str, list[str]]:
    raw: dict[str, list[str]] = json.loads(path.read_text(encoding="utf-8"))
    # Keys and values may be phrases; a phrase key gives a swap the context that makes it safe.
    return {normalize(word): syns for word, syns in raw.items() if not word.startswith("_")}


def match_case(template: str, word: str) -> str:
    if template.isupper() and len(template) > 1:
        return word.upper()
    if template[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def phrase_fits(pre: str, matches: list[re.Match[str]], i: int, j: int) -> bool:
    """Whether the words at [i, j) can be merged: unpunctuated, and not ending a clause or a main-verb "had"/"have"."""
    if j >= len(matches):
        return False
    gaps = (pre[matches[n].end() : matches[n + 1].start()] for n in range(i, j))
    if any(gap.strip() for gap in gaps):
        return False
    return not (normalize(matches[j - 1].group()) in {"had", "have"} and normalize(matches[j].group()) in MAIN_VERB_OBJECTS)


def watermark(
    text: str,
    key: bytes,
    synonyms: dict[str, list[str]],
    target: float,
    max_seconds: float,
    max_substitutions: int = 0,
) -> WatermarkResult:
    """Greedy edits in synonym-list order, left to right within each entry.

    Stops when the green fraction reaches `target`, the time budget runs out, the substitution cap is hit,
    or no edit is left. Every edit raises the green fraction, so the final text is the best seen.
    """
    start = time.monotonic()
    pre = preprocess(text)
    matches = list(iter_word_matches(pre))
    if not matches:
        raise ValueError("input contains no words")
    norm = [normalize(m.group()) for m in matches]
    colors = [word_color(w, key) for w in norm]
    total = len(matches)
    green = sum(c == GREEN for c in colors)
    initial = green / total

    # List order is the edit order, so riskier entries placed last are used only when the target needs them.
    spans = [
        (i, i + len(phrase.split()))
        for phrase in synonyms
        for i in range(len(matches))
        if norm[i : i + len(phrase.split())] == phrase.split()
    ]
    edits: dict[int, tuple[int, str]] = {}
    used: set[int] = set()
    stop_reason = "no_more_candidates"
    for i, j in spans:
        if green / total >= target:
            stop_reason = "target_reached"
            break
        if time.monotonic() - start > max_seconds:
            stop_reason = "time_limit"
            break
        if max_substitutions and len(edits) >= max_substitutions:
            stop_reason = "substitution_limit"
            break
        options = synonyms.get(" ".join(norm[i:j]), [])
        if not options or used.intersection(range(i, j)) or (j - i > 1 and not phrase_fits(pre, matches, i, j)):
            continue
        choice = max(options, key=lambda s: sum(word_color(w, key) == GREEN for w in words(s)))
        replacement = words(choice)
        new_green = green - sum(colors[n] == GREEN for n in range(i, j)) + sum(
            word_color(w, key) == GREEN for w in replacement
        )
        new_total = total - (j - i) + len(replacement)
        if new_green * total <= green * new_total:
            continue
        edits[i] = (j, match_case(matches[i].group(), choice))
        used.update(range(i, j))
        green, total = new_green, new_total
    else:
        if green / total >= target:
            stop_reason = "target_reached"

    out = pre
    for i in sorted(edits, reverse=True):
        j, new = edits[i]
        out = out[: matches[i].start()] + new + out[matches[j - 1].end() :]

    return WatermarkResult(
        text=out,
        initial_fraction=initial,
        final_fraction=green / total,
        reached_target=green / total >= target,
        stop_reason=stop_reason,
        elapsed_seconds=time.monotonic() - start,
        substitutions=[
            Substitution(i, " ".join(m.group() for m in matches[i : j]), new) for i, (j, new) in sorted(edits.items())
        ],
    )
