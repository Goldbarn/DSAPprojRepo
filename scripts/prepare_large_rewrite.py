"""Freeze 100 fresh-to-rewriting passages. Run: uv run python scripts/prepare_large_rewrite.py."""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from wmark.records import read_jsonl, write_csv, write_jsonl
from wmark.color import load_key
from wmark.settings import CANDIDATES_PATH, KEY_PATH, RESULTS_DIR, ROOT, SPLITS_DIR, load_settings

OUT = RESULTS_DIR / "rewrite" / "large-test"
COUNT = 100
SEED = load_settings().seed + 2


def prepare(out: Path) -> None:
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite frozen test: {out}")
    splits = sorted(SPLITS_DIR.glob("*.jsonl"))
    used = {p["id"] for split in splits for p in read_jsonl(split)}
    calibration = {
        p["source_id"] for split in splits if split.stem.startswith("calibration") for p in read_jsonl(split)
    }
    pools = {}
    for passage in read_jsonl(CANDIDATES_PATH):
        if (
            passage["id"] not in used
            and passage["source_id"] not in calibration
            and passage["length_group"] == "100-199"
        ):
            pools.setdefault(passage["source_id"], []).append(passage)
    rng = random.Random(SEED)
    sources = sorted(pools)
    for source in sources:
        pools[source].sort(key=lambda p: p["id"])
        rng.shuffle(pools[source])
    selected = []
    while len(selected) < COUNT:
        available = [source for source in sources if pools[source]]
        if not available:
            raise ValueError("Not enough eligible passages")
        rng.shuffle(available)
        for source in available:
            selected.append(pools[source].pop())
            if len(selected) == COUNT:
                break
    assert len({p["id"] for p in selected}) == COUNT
    assert not used.intersection(p["id"] for p in selected)
    assert not calibration.intersection(p["source_id"] for p in selected)
    out.mkdir(parents=True)
    write_jsonl(out / "passages.jsonl", selected)
    (out / "original").mkdir()
    (out / "watermarked").mkdir()
    for passage in selected:
        (out / "original" / f"{passage['id']}.txt").write_text(passage["text"], encoding="utf-8")
    procedure = ROOT / "results" / "rewrite" / "PROCEDURE.md"
    (out / "PROCEDURE.md").write_bytes(procedure.read_bytes())
    (out / "settings.toml").write_bytes((ROOT / "config" / "settings_v3.toml").read_bytes())
    inputs = [CANDIDATES_PATH, procedure, ROOT / "config" / "settings_v3.toml", *splits]
    manifest = {
        "seed": SEED, "count": COUNT, "length_group": "100-199",
        "source_counts": dict(sorted(Counter(p["source_id"] for p in selected).items())),
        "input_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "passages_sha256": hashlib.sha256((out / "passages.jsonl").read_bytes()).hexdigest(),
        "key_sha256": hashlib.sha256(load_key(KEY_PATH)).hexdigest(),
        "status": "prepared; no rewriting or quality review performed",
        "limitation": "Fresh to rewriting, but drawn from the previously scored evaluation-source pool.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    labels = list(selected)
    rng.shuffle(labels)
    write_csv(out / "review_key.csv", [{"label": f"L{i:03}", "id": p["id"]} for i, p in enumerate(labels, 1)])
    write_csv(out / "review_sheet.csv", [
        {"label": f"L{i:03}", "reviewer": "", "meaning_preserved": "", "readable": "", "notes": ""}
        for i in range(1, COUNT + 1)
    ])
    write_csv(out / "editing_log.csv", [
        {"id": p["id"], "editor": "", "elapsed_seconds": "", "stop_reason": ""} for p in selected
    ])
    print(f"Prepared {COUNT} passages from {len(sources)} sources in {out}")


if __name__ == "__main__":
    prepare(OUT)
