"""Count flagged passages by threshold across every calibration-source candidate.

This is the evidence for the length-based thresholds in config/settings_v2.toml. It scores no evaluation-source text.
Writes results/calibration/pool_thresholds.csv.
"""

import json

from wmark.color import load_key
from wmark.detector import detect, is_flagged
from wmark.records import LENGTH_GROUPS, read_jsonl, write_csv
from wmark.settings import CANDIDATES_PATH, KEY_PATH, RESULTS_DIR, SPLITS_DIR

THRESHOLDS = [0.50 + i * 0.02 for i in range(11)]


def main() -> None:
    key = load_key(KEY_PATH)
    manifest = json.loads((SPLITS_DIR / "manifest.json").read_text(encoding="utf-8"))
    calibration = set(manifest["sources"]["calibration"])
    pool = [p for p in read_jsonl(CANDIDATES_PATH) if p["source_id"] in calibration]
    scored = [(p["length_group"], detect(p["text"], key, 0.5)) for p in pool]
    rows = []
    for t in THRESHOLDS:
        for group in LENGTH_GROUPS:
            in_group = [d for g, d in scored if g == group]
            flagged = sum(is_flagged(d.green, d.total, round(t, 2)) for d in in_group)
            rows.append({"threshold": f"{t:.2f}", "length_group": group, "flagged": flagged, "tested": len(in_group)})
    write_csv(RESULTS_DIR / "calibration" / "pool_thresholds.csv", rows)
    print(f"scored {len(pool)} passages")


if __name__ == "__main__":
    main()
