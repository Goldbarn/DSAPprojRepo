"""Draw 20 new watermarking passages, one per source, for a broader test of sentence rewriting.

Sources come from the evaluation side of the split. Passages already used or scored by any run are excluded.
"""

import random

from wmark.records import read_jsonl, write_jsonl
from wmark.settings import CANDIDATES_PATH, SPLITS_DIR, load_settings

COUNT = 20
GROUP = "100-199"


def main() -> None:
    splits = ["calibration_unmarked", "calibration_wm", "evaluation_unmarked", "evaluation_wm", "fresh_unmarked"]
    used = {p["id"] for s in splits for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    calibration = {p["source_id"] for s in splits[:2] for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    pool = [
        c
        for c in read_jsonl(CANDIDATES_PATH)
        if c["id"] not in used and c["source_id"] not in calibration and c["length_group"] == GROUP
    ]
    rng = random.Random(load_settings().seed + 1)
    sources = rng.sample(sorted({c["source_id"] for c in pool}), COUNT)
    write_jsonl(SPLITS_DIR / "fresh_wm.jsonl", [rng.choice([c for c in pool if c["source_id"] == s]) for s in sources])


if __name__ == "__main__":
    main()
