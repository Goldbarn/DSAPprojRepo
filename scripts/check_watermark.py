"""Self-check for watermark edits. Run: uv run python scripts/check_watermark.py"""

from wmark.color import GREEN, word_color
from wmark.detector import detect
from wmark.watermark import watermark

KEY = bytes(32)
RED = next(w for w in ("alpha", "beta", "gamma", "delta", "theta") if word_color(w, KEY) != GREEN)
GREENS = [w for w in ("alpha", "beta", "gamma", "delta", "theta", "kappa", "sigma", "omega") if word_color(w, KEY) == GREEN]
G = GREENS[0]

# One-word swap reaches the target and stops.
r = watermark(f"{RED} {RED} {G} {G}", KEY, {RED: [G]}, 0.75, 60)
assert r.text == f"{G} {RED} {G} {G}" and r.reached_target and r.final_fraction == detect(r.text, KEY, 0.5).green_fraction

# Phrase key and multi-word value keep the running score equal to a fresh score of the output.
r = watermark(f"{RED} {RED} tail", KEY, {f"{RED} {RED}": [f"{G} {G} {G}"]}, 0.99, 60)
assert r.text == f"{G} {G} {G} tail" and abs(r.final_fraction - detect(r.text, KEY, 0.5).green_fraction) < 1e-9

# Phrases do not merge across punctuation, before a clause end, or into a main-verb "had".
for text in (f"{RED}, {RED} tail", f"tail {RED} {RED}", f"{RED} {RED}, tail"):
    assert watermark(text, KEY, {f"{RED} {RED}": [G]}, 0.99, 60).substitutions == []
assert watermark("x had a dog", KEY, {"x had": [G]}, 0.99, 60).substitutions == []

# An edit that does not raise the score is refused.
assert watermark(f"{G} tail", KEY, {G: [RED]}, 0.99, 60).substitutions == []

# Case follows the replaced word; list order is edit order.
assert watermark(f"{RED.title()} tail", KEY, {RED: [G]}, 0.99, 60).text == f"{G.title()} tail"
print("ok")
