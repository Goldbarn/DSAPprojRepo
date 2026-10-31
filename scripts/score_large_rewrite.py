"""Freeze and score all 100 rewrites, then build a blind review packet. Quality results remain pending.

Run: uv run python scripts/score_large_rewrite.py
"""

import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from wmark.color import load_key
from wmark.detector import detect
from wmark.records import read_csv, read_jsonl, write_csv
from wmark.settings import KEY_PATH, RESULTS_DIR, Settings, load_settings
from wmark.text import changed_words, words

OUT = RESULTS_DIR / "rewrite" / "large-test"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_pairs(passages: list[dict], run: Path, key: bytes, settings: Settings) -> list[dict]:
    ids = [p["id"] for p in passages]
    actual = {p.stem for p in (run / "watermarked").glob("*.txt")}
    if len(set(ids)) != len(ids) or actual != set(ids):
        raise ValueError(f"Output cohort mismatch: missing={set(ids) - actual}, extra={actual - set(ids)}")
    rows = []
    detector = settings.raw["detector"]
    for p in passages:
        edited = (run / "watermarked" / f"{p['id']}.txt").read_text(encoding="utf-8")
        before_threshold = (
            detector["short_threshold"] if len(words(p["text"])) < detector["short_below"] else settings.threshold
        )
        after_threshold = (
            detector["short_threshold"] if len(words(edited)) < detector["short_below"] else settings.threshold
        )
        before, after = detect(p["text"], key, before_threshold), detect(edited, key, after_threshold)
        rows.append({
            "id": p["id"], "source_id": p["source_id"], "total_before": before.total, "total": after.total,
            "green_before": before.green, "green_after": after.green,
            "score_before": f"{before.green_fraction:.6f}", "score_after": f"{after.green_fraction:.6f}",
            "threshold_before": before_threshold, "threshold_after": after_threshold,
            "flagged_before": before.flagged, "flagged_after": after.flagged,
            "reached_target": after.green_fraction >= settings.target,
            "changed_words": changed_words(p["text"], edited),
        })
    return rows


def clustered_interval(rows: list[dict], seed: int) -> tuple[float, float]:
    books = defaultdict(list)
    for row in rows:
        books[row["source_id"]].append(row["flagged_after"])
    groups = list(books.values())
    rng = random.Random(seed)
    rates = []
    for _ in range(10000):
        sample = [value for group in rng.choices(groups, k=len(groups)) for value in group]
        rates.append(sum(sample) / len(sample))
    rates.sort()
    return rates[249], rates[9749]


def main() -> None:
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    key = load_key(KEY_PATH)
    if hashlib.sha256(key).hexdigest() != manifest["key_sha256"]:
        raise ValueError("Frozen watermark key changed")
    if digest(OUT / "passages.jsonl") != manifest["passages_sha256"]:
        raise ValueError("Frozen cohort hash changed")
    for local, original in [
        ("PROCEDURE.md", "results/rewrite/PROCEDURE.md"), ("settings.toml", "config/settings_v3.toml")
    ]:
        if digest(OUT / local) != manifest["input_sha256"][original]:
            raise ValueError(f"Frozen {local} hash changed")
    passages = read_jsonl(OUT / "passages.jsonl")
    if len(passages) != manifest["count"] or len(passages) != 100:
        raise ValueError("Expected the complete frozen 100-passage cohort")
    for p in passages:
        if (OUT / "original" / f"{p['id']}.txt").read_text(encoding="utf-8") != p["text"]:
            raise ValueError(f"Original text changed: {p['id']}")
    settings = load_settings(OUT / "settings.toml")
    rows = score_pairs(passages, OUT, key, settings)
    logs = [row for batch in sorted(OUT.glob("editing_log_batch_*.csv")) for row in read_csv(batch)]
    ids = {p["id"] for p in passages}
    if len(logs) != 100 or {r["id"] for r in logs} != ids:
        raise ValueError("Editing logs must cover every passage exactly once")
    for row in logs:
        elapsed = float(row["elapsed_seconds"])
        if not 0 < elapsed <= settings.max_seconds or not row["editor"] or not row["stop_reason"]:
            raise ValueError(f"Invalid editing log for {row['id']}")
    labels = read_csv(OUT / "review_key.csv")
    if len(labels) != 100 or {r["id"] for r in labels} != ids or len({r["label"] for r in labels}) != 100:
        raise ValueError("Review labels do not match the frozen cohort")
    review = read_csv(OUT / "review_sheet.csv")
    if len(review) != 100 or {r["label"] for r in review} != {r["label"] for r in labels}:
        raise ValueError("Review sheet labels do not match the frozen mapping")
    outputs = {p.name: digest(p) for p in sorted((OUT / "watermarked").glob("*.txt"))}
    fingerprint = {"output_sha256": outputs, "key_sha256": hashlib.sha256(key).hexdigest(),
                   "review_key_sha256": digest(OUT / "review_key.csv"),
                   "procedure_sha256": digest(OUT / "PROCEDURE.md"), "settings_sha256": digest(OUT / "settings.toml")}
    freeze_path = OUT / "output_manifest.json"
    if freeze_path.exists():
        previous = json.loads(freeze_path.read_text(encoding="utf-8"))
        if any(previous[k] != v for k, v in fingerprint.items()):
            raise ValueError("Frozen outputs or experiment inputs changed; refusing to replace results")
    else:
        fingerprint["frozen_at_utc"] = datetime.now(timezone.utc).isoformat()
        freeze_path.write_text(json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8")
    write_csv(OUT / "wm_scores.csv", rows)
    log_by_id = {r["id"]: r for r in logs}
    write_csv(OUT / "editing_log.csv", [log_by_id[p["id"]] for p in passages])
    originals = {p["id"]: p["text"] for p in passages}
    packet = [
        "# Blind quality review", "",
        "For each pair, answer whether the main meaning is preserved and the prose is readable.",
        "Record answers in review_sheet.csv. Do not open other experiment files before completing the review.", ""
    ]
    for r in labels:
        edited = (OUT / "watermarked" / f"{r['id']}.txt").read_text(encoding="utf-8")
        packet.extend([
            f"## {r['label']}", "", "### Original", "", originals[r["id"]], "", "### Rewritten", "", edited, ""
        ])
    (OUT / "review_pairs.md").write_text("\n".join(packet), encoding="utf-8")
    by_book = []
    for source in sorted({r["source_id"] for r in rows}):
        group = [r for r in rows if r["source_id"] == source]
        by_book.append({"source_id": source, "tested": len(group), "flagged": sum(r["flagged_after"] for r in group)})
    write_csv(OUT / "by_source.csv", by_book)
    low, high = clustered_interval(rows, manifest["seed"])
    flagged = sum(r["flagged_after"] for r in rows)
    initially_unflagged = [r for r in rows if not r["flagged_before"]]
    summary = ["# Large rewriting test: detection results", "",
        f"- Frozen outputs: 100 passages from {len(by_book)} books.",
        f"- Flagged after rewriting: {flagged}/100 ({flagged}%).",
        f"- Flagged before rewriting: {sum(r['flagged_before'] for r in rows)}/100.",
        f"- Newly flagged among initially unflagged passages: "
        f"{sum(r['flagged_after'] for r in initially_unflagged)}/{len(initially_unflagged)}.",
        f"- Reached target 0.57: {sum(r['reached_target'] for r in rows)}/100. "
        "This target alone does not imply detection for short outputs.",
        f"- Approximate 95% detection interval: {low:.1%} to {high:.1%} (10,000 whole-book bootstrap resamples).",
        f"- Median changed words: {median(r['changed_words'] for r in rows):g}.",
        f"- Outputs changed: {sum(r['changed_words'] > 0 for r in rows)}/100; "
        f"originals retained: {sum(r['changed_words'] == 0 for r in rows)}/100.",
        "- Timing observations are in editing_log.csv. Early shared-batch intervals overlap, and some exclude "
        "initial reading. No aggregate editing-time estimate is reported.",
        "- Meaning preservation, readability, and usable-and-flagged success: pending independent teammate review.", "",
        "Send only review_pairs.md and review_sheet.csv to the reviewer. Keep review_key.csv, wm_scores.csv, "
        "and other experiment files hidden until answers are recorded.", "",
        "This run uses three parallel editor instances under the same frozen rules, so it is not an exact "
        "replication of the earlier single-editor run. Editing times are wall-clock observations, "
        "not API latency benchmarks.",
        "The passages are fresh to rewriting but drawn from an already scored pool. This within-corpus test "
        "does not establish performance on unseen books or student writing.", ""]
    (OUT / "summary.md").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
