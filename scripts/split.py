"""Divide candidates into calibration and evaluation sets, by source document, before any scoring.

Every passage from a source lands in the same set. Also selects the 5 query-access forgery passages
from the 10 evaluation watermarking passages with a seeded random draw. Run once; re-splitting after
seeing scores would bias the results.
"""

import argparse
import json
import random
from collections import Counter, defaultdict

from wmark.records import LENGTH_GROUPS, read_jsonl, write_jsonl
from wmark.settings import CANDIDATES_PATH, SPLITS_DIR, load_settings

UNMARKED_PER_GROUP = 50  # 150 per set; spec requires at least 30 per group
WM_GROUP = "100-199"
WM_COUNT = {"calibration": 5, "evaluation": 10}
FORGERY_COUNT = 5


def needs(set_name: str) -> dict[str, int]:
    need = dict.fromkeys(LENGTH_GROUPS, UNMARKED_PER_GROUP)
    need[WM_GROUP] += WM_COUNT[set_name]
    return need


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite an existing split")
    args = parser.parse_args()

    manifest_path = SPLITS_DIR / "manifest.json"
    if manifest_path.exists() and not args.force:
        raise SystemExit(f"{manifest_path} exists; refusing to re-split (use --force only before any scoring)")

    seed = load_settings().seed
    rng = random.Random(seed)
    candidates = read_jsonl(CANDIDATES_PATH)
    by_source = defaultdict(list)
    for c in candidates:
        by_source[c["source_id"]].append(c)

    sources = sorted(by_source)
    rng.shuffle(sources)
    assignment: dict[str, list[str]] = {"calibration": [], "evaluation": []}
    have = {"calibration": Counter(), "evaluation": Counter()}
    for s in sources:
        calib_short = any(have["calibration"][g] < n for g, n in needs("calibration").items())
        target = "calibration" if calib_short else "evaluation"
        assignment[target].append(s)
        have[target].update(c["length_group"] for c in by_source[s])

    for set_name in assignment:
        for g, n in needs(set_name).items():
            if have[set_name][g] < n:
                raise SystemExit(f"{set_name}: need {n} candidates in {g}, have {have[set_name][g]}; add sources")

    manifest = {"seed": seed, "sources": assignment, "counts": {}, "forgery": {}}
    for set_name, srcs in assignment.items():
        pool = [c for s in sorted(srcs) for c in by_source[s]]
        wm = rng.sample([c for c in pool if c["length_group"] == WM_GROUP], WM_COUNT[set_name])
        wm_ids = {c["id"] for c in wm}
        unmarked = []
        for g in LENGTH_GROUPS:
            group = [c for c in pool if c["length_group"] == g and c["id"] not in wm_ids]
            unmarked += rng.sample(group, UNMARKED_PER_GROUP)
        write_jsonl(SPLITS_DIR / f"{set_name}_unmarked.jsonl", unmarked)
        write_jsonl(SPLITS_DIR / f"{set_name}_wm.jsonl", wm)
        manifest["counts"][set_name] = {
            "unmarked": len(unmarked),
            "unmarked_by_group": Counter(c["length_group"] for c in unmarked),
            "wm": len(wm),
            "source_documents": len({c["source_id"] for c in unmarked + wm}),
        }

    eval_wm = read_jsonl(SPLITS_DIR / "evaluation_wm.jsonl")
    forgery_ids = sorted(rng.sample([c["id"] for c in eval_wm], FORGERY_COUNT))
    manifest["forgery"] = {
        "ids": forgery_ids,
        "method": f"random.Random({seed}) draw of {FORGERY_COUNT} from the 10 evaluation watermarking passages, "
        "made after the split and before any detector scoring",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
