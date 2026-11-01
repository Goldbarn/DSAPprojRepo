"""Export paper-sized PNG tables and existing graphs without changing the report.

Run: uv run --group report python scripts/export_m1_paper_assets.py
"""

import textwrap
from zipfile import ZIP_DEFLATED, ZipFile

import figures
from matplotlib import pyplot as plt

from wmark.records import LENGTH_GROUPS, read_csv, read_jsonl
from wmark.settings import ROOT, SPLITS_DIR

OUT = ROOT / "report" / "figures" / "m1-paper"
CAL = ROOT / "results" / "calibration" / "run-20261031-123747"
EVAL = figures.FIRST


def table(name: str, title: str, columns: list[str], rows: list[list[str]], widths: list[float],
          height: float, note: str = "", fontsize: float = 10) -> None:
    fig, ax = plt.subplots(figsize=(6.5, height), facecolor="white")
    ax.axis("off")
    ax.text(0, 1, title, transform=ax.transAxes, fontsize=11, weight="bold", va="top", color="#111111")
    grid = ax.table(cellText=rows, colLabels=columns, colWidths=widths, cellLoc="left",
                    colLoc="left", bbox=(0, 0.17 if note else 0.02, 1, 0.69 if note else 0.84))
    grid.auto_set_font_size(False)
    grid.set_fontsize(fontsize)
    multiline = any("\n" in value for row in rows for value in row)
    for (row, _), cell in grid.get_celld().items():
        cell.set_edgecolor("#c9c9c9")
        cell.set_linewidth(0.6)
        cell.PAD = 0.055
        cell.set_text_props(color="#111111", fontfamily="DejaVu Sans")
        cell.set_facecolor("#eeeeee" if row == 0 else "white")
        if row == 0:
            cell.set_text_props(weight="bold")
        if multiline:
            cell.set_height(0.10 if row == 0 else 0.90 / len(rows))
    if note:
        ax.text(0, 0.025, note, transform=ax.transAxes, fontsize=8, va="bottom", color="#333333")
    fig.subplots_adjust(left=0.015, right=0.985, top=0.97, bottom=0.03)
    fig.savefig(OUT / name, dpi=400, facecolor="white")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sweep = read_csv(CAL / "threshold_sweep.csv")
    table("calibration_thresholds.png", "Calibration threshold comparison",
          ["Threshold", "Flagged unmarked", "Unflagged outputs"],
          [[f"{float(r['threshold']):.2f}", f"{r['flagged_unmarked']} / {r['unmarked_tested']}",
            f"{r['unflagged_wm_outputs']} / {r['wm_tested']}"] for r in sweep],
          [0.2, 0.4, 0.4], 1.65, "Threshold 0.55 selected; watermarking target 0.56.")
    unmarked = read_csv(EVAL / "unmarked_scores.csv")
    wm = read_csv(EVAL / "wm_scores.csv")
    reviews = {r["id"]: r for r in read_csv(EVAL / "review_sheet.csv")}
    assert len(unmarked) == 150 and len(wm) == len(reviews) == 10
    flagged = sum(r["flagged_after"] == "True" for r in wm)
    usable = sum(r["flagged_after"] == "True" and reviews[r["id"]]["meaning_preserved"] == "yes"
                 and reviews[r["id"]]["readable"] == "yes" for r in wm)
    false = sum(r["flagged"] == "True" for r in unmarked)
    table("primary_results.png", "Primary evaluation: fixed threshold 0.55", ["Measurement", "Result"],
          [["Unmarked false-positive rate", f"{false} / 150 = {false / 150:.1%}"],
           ["Detection rate on watermarking outputs", f"{flagged} / 10 = {flagged / 10:.0%}"],
           ["Usable and flagged (proxy review)", f"{usable} / 10 = {usable / 10:.0%}"]],
          [0.74, 0.26], 1.55, "Proxy quality judgments; required teammate review remains outstanding.")
    table("length_group_results.png", "Unmarked evaluation results by passage length",
          ["Normalized words", "Flagged", "Tested", "False-positive rate"],
          [[g, str(sum(r["flagged"] == "True" for r in unmarked if r["length_group"] == g)),
            str(sum(r["length_group"] == g for r in unmarked)),
            f"{sum(r['flagged'] == 'True' for r in unmarked if r['length_group'] == g) / sum(r['length_group'] == g for r in unmarked):.0%}"]
           for g in LENGTH_GROUPS], [0.3, 0.16, 0.16, 0.38], 1.55,
          "Threshold 0.55. Zero observed flags does not establish zero false-positive risk.")
    counts = [[str(len(read_jsonl(SPLITS_DIR / f"{phase}_{kind}.jsonl")))
               for phase in ("calibration", "evaluation")] for kind in ("unmarked", "wm")]
    table("data_allocation.png", "Experiment allocation: 315 distinct passages",
          ["Collection", "Calibration", "Evaluation"],
          [["Unmarked prose", *counts[0]], ["Selected for watermarking", *counts[1]]],
          [0.56, 0.22, 0.22], 1.45,
          "Unmarked sets: 50 passages per length group in each set. Books do not cross sets.")
    cells = [
        ["Removal", "Attack: paraphrase blindly.\nCost: 0 queries; edits uncertain.\nQuality: extensive edits risk meaning.\nDefense: larger score margin.",
         "Attack: test substitutions.\nCost: up to 100 queries and 15 minutes in later tests.\nQuality: must be checked.\nDefense: rate limits; binary replies.",
         "Attack: replace green words with red alternatives.\nCost: 0 discovery queries.\nQuality: suitable synonyms needed.\nDefense: protect the key."],
        ["Forgery", "Attack: make blind substitutions.\nCost: 0 queries; edits uncertain.\nQuality: awkward edits possible.\nDefense: threshold above typical unmarked scores.",
         "Attack: query repeated words to learn colors.\nCost: 1 query per tested word, plus editing.\nQuality: suitable synonyms needed.\nDefense: limit query access.",
         "Attack: apply keyed watermarking.\nCost: 0 discovery queries.\nQuality: primary outputs failed proxy review.\nDefense: protect the key."],
    ]
    wrapped = [[row[0], *["\n".join(textwrap.fill(part, width=29) for part in cell.splitlines())
                         for cell in row[1:]]] for row in cells]
    table("threat_model.png", "Threat model: attacks, costs, quality, and defenses",
          ["Goal", "No detector access", "Query access", "Key access"], wrapped,
          [0.12, 0.29, 0.30, 0.29], 4.7,
          "Attack effectiveness and budgets are predictions, not measured attack-success results.\n"
          "Removal requires a flagged, usable starting output. Neither response hiding nor rate limits guarantees safety.",
          fontsize=8)
    figures.OUT = OUT
    plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white", "font.family": "DejaVu Sans"})
    for draw, name in [(figures.watermarking, "watermarking_scores.png"),
                       (figures.false_positives, "false_positives.png"),
                       (figures.broader_test, "broader_test.png")]:
        draw()
        if name == "broader_test.png":
            fig = plt.gcf()
            fig.set_size_inches(6.5, 2.9)
            fig.subplots_adjust(bottom=0.22)
            fig.text(0.02, 0.025, "Separate post-evaluation run; quality judgments come from proxy reviews.",
                     fontsize=8, color="#333333")
        plt.gcf().savefig(OUT / name, dpi=400, facecolor="white")
        plt.close("all")
    captions = """# Milestone 1 PNG assets

All images are exported at 400 dpi on white backgrounds. Most are 6.5 inches wide;
false_positives.png is 4.6 inches wide. Insert at the intended width to preserve text size.
Keep captions as document text and assign table/figure numbers in the final paper.
Replace existing Markdown tables with their PNG versions rather than duplicating them.

## Recommended core assets and captions

- data_allocation.png, under Implementation: Allocation of 315 distinct passages into calibration and
  evaluation sets. Each unmarked set contains 50 passages per length group; books do not cross sets.
- calibration_thresholds.png, after threshold selection: Calibration counts for 150 unmarked passages and
  five watermarking outputs. The chosen threshold was 0.55 and the watermarking target was 0.56.
- primary_results.png, at the start of Evaluation: Primary evaluation at the frozen threshold of 0.55.
  Usability is based on proxy review; the required independent teammate review remains outstanding.
- watermarking_scores.png, after the headline results: Green fractions before and after watermarking
  for all ten primary evaluation attempts. The line marks 0.55; hollow output markers were not flagged.
- length_group_results.png, with the length discussion: Flagged and tested unmarked passages by
  normalized-word length. No flags in a group does not establish a zero population false-positive rate.
- threat_model.png, under Threat Model: Predicted attacks under no, query, and key access. Query limits
  are proposed budgets, not measured attack-success results. Removal requires a flagged, usable starting text.

## Optional post-evaluation figures

- false_positives.png: False positives among 1,500 fresh unmarked passages, with 500 per length group.
  The original threshold is 0.55; length-based thresholds are 0.68 below 100 words and 0.56 otherwise.
- broader_test.png: Three watermarking methods on 20 new passages, one per book. Meaning and readability
  are separate proxy judgments. Usable and flagged requires both quality answers and a detector flag.

For a tight six-page report, prioritize the primary score graph, length-group table, and required threat-model
table. The small allocation, calibration, and primary-result tables can replace existing tables. Include the
optional graphs only if retaining their post-evaluation discussion. The separate 100-passage run is not included.
"""
    (OUT / "CAPTIONS.md").write_text(captions, encoding="utf-8")
    archive = OUT / "m1-paper-pngs.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for path in sorted(OUT.glob("*.png")):
            bundle.write(path, path.name)
        bundle.write(OUT / "CAPTIONS.md", "CAPTIONS.md")
    print(f"Exported {len(list(OUT.glob('*.png')))} PNGs at 400 dpi and {archive}")


if __name__ == "__main__":
    main()
