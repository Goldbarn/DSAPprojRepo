import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from wmark.color import GREEN, word_color
from wmark.text import iter_word_matches, normalize, preprocess, words


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
    # Keep only single-word synonyms so substitutions never change the word count.
    return {
        normalize(word): [s for s in syns if len(words(s)) == 1]
        for word, syns in raw.items()
        if not word.startswith("_")
    }


def match_case(template: str, word: str) -> str:
    if template.isupper() and len(template) > 1:
        return word.upper()
    if template[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def watermark(
    text: str,
    key: bytes,
    synonyms: dict[str, list[str]],
    target: float,
    max_seconds: float,
    max_substitutions: int = 0,
) -> WatermarkResult:
    """Greedy left-to-right replacement of red words with green synonyms.

    Stops when the green fraction reaches `target`, the time budget runs out, the substitution cap is hit,
    or no red word has a green synonym. Every substitution is red -> green, so the final text is the best seen.
    """
    start = time.monotonic()
    pre = preprocess(text)
    matches = list(iter_word_matches(pre))
    if not matches:
        raise ValueError("input contains no words")
    total = len(matches)
    green = sum(1 for m in matches if word_color(normalize(m.group()), key) == GREEN)
    initial = green / total

    replacements: dict[int, str] = {}
    stop_reason = "no_more_candidates"
    for i, m in enumerate(matches):
        if green / total >= target:
            stop_reason = "target_reached"
            break
        if time.monotonic() - start > max_seconds:
            stop_reason = "time_limit"
            break
        if max_substitutions and len(replacements) >= max_substitutions:
            stop_reason = "substitution_limit"
            break
        w = normalize(m.group())
        if word_color(w, key) == GREEN:
            continue
        choice = next((s for s in synonyms.get(w, []) if word_color(normalize(s), key) == GREEN), None)
        if choice is not None:
            replacements[i] = match_case(m.group(), choice)
            green += 1
    else:
        if green / total >= target:
            stop_reason = "target_reached"

    out = pre
    for i in sorted(replacements, reverse=True):
        m = matches[i]
        out = out[: m.start()] + replacements[i] + out[m.end() :]

    return WatermarkResult(
        text=out,
        initial_fraction=initial,
        final_fraction=green / total,
        reached_target=green / total >= target,
        stop_reason=stop_reason,
        elapsed_seconds=time.monotonic() - start,
        substitutions=[Substitution(i, matches[i].group(), r) for i, r in sorted(replacements.items())],
    )
