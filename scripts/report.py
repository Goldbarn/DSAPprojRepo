"""Summarize a run directory after the quality review sheet has been filled in.

Writes summary.md with the Section 4.2 measurements: false-positive rate, detection rate, usable watermarking
success rate, per-length-group counts, the 3/n zero-error bound, and the most repetitive passage.
"""

import argparse
from collections import defaultdict
from pathlib import Path

from wmark.records import LENGTH_GROUPS, read_csv

YES = {"y", "yes", "true", "1"}


def truthy(v: str) -> bool:
    return v.strip().lower() in YES


def rate(k: int, n: int) -> str:
    if n == 0:
        return "not applicable (n = 0)"
    bound = f"; zero-error 95% upper bound 3/n = {3 / n:.1%}" if k == 0 else ""
    return f"{k}/{n} = {k / n:.1%}{bound}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--pending", action="store_true", help="summarize before the quality review is finished")
    args = parser.parse_args()

    unmarked = read_csv(args.run_dir / "unmarked_scores.csv")
    wm = read_csv(args.run_dir / "wm_scores.csv")
    review = {r["id"]: r for r in read_csv(args.run_dir / "review_sheet.csv")}

    missing = [pid for pid, r in review.items() if not (r["meaning_preserved"] and r["readable"] and r["reviewer"])]
    if missing and not args.pending:
        raise SystemExit(f"review sheet incomplete for: {', '.join(missing)}")

    flagged_unmarked = sum(truthy(r["flagged"]) for r in unmarked)
    flagged_wm = sum(truthy(r["flagged_after"]) for r in wm)
    usable = {pid for pid, r in review.items() if truthy(r["meaning_preserved"]) and truthy(r["readable"])}
    usable_flagged = sum(truthy(r["flagged_after"]) and r["id"] in usable for r in wm)
    reached = sum(truthy(r["reached_target"]) for r in wm)

    lines = [f"# Summary: {args.run_dir.name}", "", "## Headline measurements", ""]
    lines += [
        f"- Unmarked false-positive rate: {rate(flagged_unmarked, len(unmarked))}",
        f"- Detection rate on watermarking outputs: {rate(flagged_wm, len(wm))}",
        f"- Usable watermarking success rate: {'pending review' if missing else rate(usable_flagged, len(wm))}",
        f"- Attempts reaching the target: {reached}/{len(wm)}",
        f"- Unmarked source documents: {len({r['source_id'] for r in unmarked})}",
        "",
        "## Unmarked passages by length group",
        "",
        "| Group | Flagged | Tested |",
        "| --- | ---: | ---: |",
    ]
    by_group = defaultdict(lambda: [0, 0])
    for r in unmarked:
        by_group[r["length_group"]][0] += truthy(r["flagged"])
        by_group[r["length_group"]][1] += 1
    lines += [f"| {g} | {by_group[g][0]} | {by_group[g][1]} |" for g in LENGTH_GROUPS]

    lines += [
        "",
        "## Watermarking attempts",
        "",
        "| ID | Before | After | Flagged | Target | Stop | Changed words | Meaning | Readable |",
        "| --- | ---: | ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for r in wm:
        rv = review[r["id"]]
        lines.append(
            f"| {r['id']} | {r['score_before']} | {r['score_after']} | {r['flagged_after']} | {r['reached_target']} "
            f"| {r['stop_reason']} | {r['changed_words']} | {rv['meaning_preserved']} | {rv['readable']} |"
        )

    rep = min(unmarked, key=lambda r: int(r["distinct"]) / int(r["total"]))
    lines += [
        "",
        "## Most repetitive unmarked passage",
        "",
        f"- {rep['id']}: {rep['distinct']} distinct / {rep['total']} total words, "
        f"score {rep['green_fraction']}, flagged {rep['flagged']}",
    ]

    (args.run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
