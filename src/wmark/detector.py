from dataclasses import dataclass
from fractions import Fraction

from wmark.color import GREEN, word_color
from wmark.text import words


class EmptyInputError(ValueError):
    pass


@dataclass(frozen=True)
class Detection:
    green: int
    total: int
    distinct: int
    threshold: float
    flagged: bool

    @property
    def green_fraction(self) -> float:
        return self.green / self.total


def is_flagged(green: int, total: int, threshold: float) -> bool:
    # Exact comparison so a score equal to the threshold is never flagged due to float rounding.
    return Fraction(green, total) > Fraction(str(threshold))


def detect(text: str, key: bytes, threshold: float) -> Detection:
    tokens = words(text)
    if not tokens:
        raise EmptyInputError("input contains no words")
    colors = {w: word_color(w, key) for w in set(tokens)}
    green = sum(1 for w in tokens if colors[w] == GREEN)
    return Detection(
        green=green,
        total=len(tokens),
        distinct=len(colors),
        threshold=threshold,
        flagged=is_flagged(green, len(tokens), threshold),
    )
