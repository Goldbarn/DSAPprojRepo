"""Back-test earlier designs on more text.

Runs both word-swap designs on the 20 passages in data/splits/fresh_wm.jsonl, and compares the single 0.55 threshold
with the length-based thresholds on every evaluation-source candidate that no earlier run used. Writes results/backtest/.
"""

from run import run_watermarking

from wmark.color import load_key
from wmark.detector import detect
from wmark.records import LENGTH_GROUPS, read_jsonl, write_csv
from wmark.settings import CANDIDATES_PATH, KEY_PATH, RESULTS_DIR, ROOT, SETTINGS_PATH, SPLITS_DIR, load_settings

OUT = RESULTS_DIR / "backtest"
SETTINGS_V2 = ROOT / "config" / "settings_v2.toml"


def main() -> None:
    key = load_key(KEY_PATH)
    fresh_wm = read_jsonl(SPLITS_DIR / "fresh_wm.jsonl")
    for name, path in (("word_swaps_v1", SETTINGS_PATH), ("word_swaps_v2", SETTINGS_V2)):
        out_dir = OUT / name
        out_dir.mkdir(parents=True, exist_ok=True)
        write_csv(out_dir / "wm_scores.csv", run_watermarking(fresh_wm, key, load_settings(path), out_dir))

    splits = ["calibration_unmarked", "calibration_wm", "evaluation_unmarked", "evaluation_wm", "fresh_unmarked", "fresh_wm"]
    used = {p["id"] for s in splits for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    calibration = {p["source_id"] for s in splits[:2] for p in read_jsonl(SPLITS_DIR / f"{s}.jsonl")}
    pool = [c for c in read_jsonl(CANDIDATES_PATH) if c["id"] not in used and c["source_id"] not in calibration]

    rows = []
    for group, (_, hi) in LENGTH_GROUPS.items():
        scored = [detect(p["text"], key, 0.55) for p in pool if p["length_group"] == group]
        length_based = 0.68 if hi < 100 else 0.56
        rows.append(
            {
                "length_group": group,
                "tested": len(scored),
                "flagged_single_055": sum(d.flagged for d in scored),
                "flagged_length_based": sum(d.green_fraction > length_based for d in scored),
            }
        )
    write_csv(OUT / "unmarked_thresholds.csv", rows)
    print(rows)


if __name__ == "__main__":
    main()
