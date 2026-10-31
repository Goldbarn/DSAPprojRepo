"""Run the calibration or evaluation phase (Section 4.2).

Writes a timestamped run directory under results/<phase>/ containing the settings snapshot, detector scores,
every watermarked output, and a blind review sheet for the quality check. Evaluation requires
settings.frozen = true.
"""

import argparse
import json
import random
import shutil
from datetime import datetime
from pathlib import Path

from wmark.color import load_key
from wmark.detector import detect, is_flagged
from wmark.records import read_jsonl, write_csv, write_jsonl
from wmark.settings import KEY_PATH, RESULTS_DIR, SETTINGS_PATH, SPLITS_DIR, SYNONYMS_PATH, load_settings
from wmark.text import changed_words
from wmark.watermark import load_synonyms, watermark

SWEEP = [0.50, 0.55, 0.60, 0.65]


def score_unmarked(passages: list[dict], key: bytes, threshold: float) -> list[dict]:
    rows = []
    for p in passages:
        d = detect(p["text"], key, threshold)
        rows.append(
            {
                "id": p["id"],
                "source_id": p["source_id"],
                "length_group": p["length_group"],
                "total": d.total,
                "distinct": d.distinct,
                "green": d.green,
                "green_fraction": f"{d.green_fraction:.6f}",
                "flagged": d.flagged,
            }
        )
    return rows


def run_watermarking(passages: list[dict], key: bytes, settings, out_dir: Path) -> list[dict]:
    synonyms = load_synonyms(SYNONYMS_PATH)
    rows, outputs = [], []
    for p in passages:
        before = detect(p["text"], key, settings.threshold)
        r = watermark(p["text"], key, synonyms, settings.target, settings.max_seconds, settings.max_substitutions)
        after = detect(r.text, key, settings.threshold)
        (out_dir / "watermarked").mkdir(parents=True, exist_ok=True)
        (out_dir / "watermarked" / f"{p['id']}.txt").write_text(r.text, encoding="utf-8")
        outputs.append({"id": p["id"], "original": p["text"], "edited": r.text})
        rows.append(
            {
                "id": p["id"],
                "source_id": p["source_id"],
                "total": after.total,
                "distinct_before": before.distinct,
                "distinct_after": after.distinct,
                "score_before": f"{before.green_fraction:.6f}",
                "flagged_before": before.flagged,
                "green_after": after.green,
                "score_after": f"{after.green_fraction:.6f}",
                "flagged_after": after.flagged,
                "reached_target": r.reached_target,
                "stop_reason": r.stop_reason,
                "substitutions": len(r.substitutions),
                "changed_words": changed_words(p["text"], r.text),
                "elapsed_seconds": f"{r.elapsed_seconds:.3f}",
            }
        )
    write_jsonl(out_dir / "watermarked.jsonl", outputs)
    return rows


def write_review_sheet(path: Path, rows: list[dict], wm_dir: Path, originals: dict[str, str], seed: int) -> None:
    order = [r["id"] for r in rows]
    random.Random(seed).shuffle(order)
    sheet = [
        {
            "id": pid,
            "original": originals[pid],
            "edited": (wm_dir / f"{pid}.txt").read_text(encoding="utf-8"),
            "reviewer": "",
            "meaning_preserved": "",
            "readable": "",
            "notes": "",
        }
        for pid in order
    ]
    write_csv(path, sheet)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["calibration", "evaluation"])
    args = parser.parse_args()

    settings = load_settings()
    if args.phase == "evaluation" and not settings.frozen:
        raise SystemExit("set [experiment] frozen = true in config/settings.toml before evaluation")
    key = load_key(KEY_PATH)

    out_dir = RESULTS_DIR / args.phase / datetime.now().strftime("run-%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True)
    shutil.copy(SETTINGS_PATH, out_dir / "settings.toml")
    shutil.copy(SYNONYMS_PATH, out_dir / "synonyms.json")

    unmarked = read_jsonl(SPLITS_DIR / f"{args.phase}_unmarked.jsonl")
    wm_passages = read_jsonl(SPLITS_DIR / f"{args.phase}_wm.jsonl")

    unmarked_rows = score_unmarked(unmarked, key, settings.threshold)
    write_csv(out_dir / "unmarked_scores.csv", unmarked_rows)

    wm_rows = run_watermarking(wm_passages, key, settings, out_dir)
    write_csv(out_dir / "wm_scores.csv", wm_rows)
    write_review_sheet(
        out_dir / "review_sheet.csv",
        wm_rows,
        out_dir / "watermarked",
        {p["id"]: p["text"] for p in wm_passages},
        settings.seed,
    )

    if args.phase == "calibration":
        sweep = []
        for t in SWEEP:
            sweep.append(
                {
                    "threshold": t,
                    "flagged_unmarked": sum(is_flagged(r["green"], r["total"], t) for r in unmarked_rows),
                    "unmarked_tested": len(unmarked_rows),
                    "unflagged_wm_outputs": sum(not is_flagged(r["green_after"], r["total"], t) for r in wm_rows),
                    "wm_tested": len(wm_rows),
                }
            )
        write_csv(out_dir / "threshold_sweep.csv", sweep)
        print(json.dumps(sweep, indent=2))

    print(f"wrote {out_dir}")
    print("Hand review_sheet.csv to a teammate who did not edit the passages. Do not share score files with them.")


if __name__ == "__main__":
    main()
