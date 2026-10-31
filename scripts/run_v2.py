"""Post-evaluation run with length-based thresholds (config/settings_v2.toml).

Measures false positives on fresh passages from evaluation sources, unscored by any earlier run, and repeats the
original 150 + 10 evaluation passages. Repeats are labeled as such: the design change was prompted by their results.
Writes to results/post-evaluation/, leaving results/evaluation/ untouched.
"""

import random
import shutil
from datetime import datetime

from run import run_watermarking, write_review_sheet

from wmark.color import load_key
from wmark.detector import detect
from wmark.records import LENGTH_GROUPS, read_jsonl, write_csv, write_jsonl
from wmark.settings import CANDIDATES_PATH, KEY_PATH, RESULTS_DIR, ROOT, SPLITS_DIR, SYNONYMS_PATH, load_settings
from wmark.text import words

SETTINGS_V2 = ROOT / "config" / "settings_v2.toml"
FRESH_PATH = SPLITS_DIR / "fresh_unmarked.jsonl"
FRESH_PER_GROUP = 500


def fresh_passages(seed: int) -> list[dict]:
    if FRESH_PATH.exists():
        return read_jsonl(FRESH_PATH)
    splits = ["calibration_unmarked", "calibration_wm", "evaluation_unmarked", "evaluation_wm"]
    used = {p["id"] for s in splits for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    calibration = {p["source_id"] for s in splits[:2] for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    pool = [c for c in read_jsonl(CANDIDATES_PATH) if c["id"] not in used and c["source_id"] not in calibration]
    rng = random.Random(seed)
    fresh = [c for g in LENGTH_GROUPS for c in rng.sample([p for p in pool if p["length_group"] == g], FRESH_PER_GROUP)]
    write_jsonl(FRESH_PATH, fresh)
    return fresh


def score(passages: list[dict], key: bytes, raw: dict) -> list[dict]:
    rows = []
    for p in passages:
        n = len(words(p["text"]))
        d = raw["detector"]
        threshold = d["short_threshold"] if n < d["short_below"] else d["threshold"]
        r = detect(p["text"], key, threshold)
        rows.append(
            {
                "id": p["id"],
                "source_id": p["source_id"],
                "length_group": p["length_group"],
                "total": r.total,
                "distinct": r.distinct,
                "green": r.green,
                "green_fraction": f"{r.green_fraction:.6f}",
                "threshold": threshold,
                "flagged": r.flagged,
            }
        )
    return rows


def main() -> None:
    settings = load_settings(SETTINGS_V2)
    key = load_key(KEY_PATH)
    out_dir = RESULTS_DIR / "post-evaluation" / datetime.now().strftime("run-%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True)
    shutil.copy(SETTINGS_V2, out_dir / "settings.toml")
    shutil.copy(SYNONYMS_PATH, out_dir / "synonyms.json")

    write_csv(out_dir / "fresh_unmarked_scores.csv", score(fresh_passages(settings.seed), key, settings.raw))
    repeat = read_jsonl(SPLITS_DIR / "evaluation_unmarked.jsonl")
    write_csv(out_dir / "repeat_unmarked_scores.csv", score(repeat, key, settings.raw))

    for name in ("calibration", "evaluation"):
        wm_passages = read_jsonl(SPLITS_DIR / f"{name}_wm.jsonl")
        phase_dir = out_dir / f"{name}_wm"
        phase_dir.mkdir()
        wm_rows = run_watermarking(wm_passages, key, settings, phase_dir)
        write_csv(phase_dir / "wm_scores.csv", wm_rows)
        originals = {p["id"]: p["text"] for p in wm_passages}
        write_review_sheet(phase_dir / "review_sheet.csv", wm_rows, phase_dir / "watermarked", originals, settings.seed)
    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
