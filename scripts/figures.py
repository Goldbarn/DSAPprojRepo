"""Draw the Milestone 1 report figures from saved runs. Run: uv run --group report python scripts/figures.py"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from wmark.records import LENGTH_GROUPS, read_csv
from wmark.settings import RESULTS_DIR, ROOT

FIRST = RESULTS_DIR / "evaluation" / "run-20261031-124055"
POST = RESULTS_DIR / "post-evaluation" / "run-20261031-124254"
OUT = ROOT / "report" / "figures"

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
# Counts from the proxy reviews in results/proxy-review and results/rewrite/review-2.
WORD_SWAPS = [7, 5, 0, 0]
REWRITING = [9, 9, 4, 4]

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def score(row: dict) -> float:
    return int(row["green"]) / int(row["total"])


def fresh_rows() -> list[dict]:
    return read_csv(POST / "fresh_unmarked_scores.csv")


def distribution() -> None:
    rows = fresh_rows()
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.3), sharex=True, sharey=True)
    bins = [0.2 + i * 0.02 for i in range(27)]
    for ax, (group, (lo, hi)) in zip(axes, LENGTH_GROUPS.items()):
        ax.hist([score(r) for r in rows if r["length_group"] == group], bins=bins, color=BLUE, edgecolor=SURFACE, lw=0.8)
        limit = 0.68 if hi < 100 else 0.56
        ax.axvline(limit, color=INK, lw=1)
        ax.text(limit + 0.01, ax.get_ylim()[1] * 0.97, f"{limit:.2f}", color=INK, va="top")
        ax.axvline(0.55, color=MUTED, lw=1, ls=":")
        ax.set_title(f"{lo}-{hi} words", fontsize=9, loc="left")
        ax.set_xlabel("Green fraction")
        ax.set_xlim(0.2, 0.75)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Unmarked passages")
    handles = [
        plt.Line2D([], [], color=INK, lw=1, label="Length-based threshold"),
        plt.Line2D([], [], color=MUTED, lw=1, ls=":", label="Original threshold 0.55"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=2, loc="lower center")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(OUT / "score_distribution.png", dpi=220)


def threshold_choice() -> None:
    rows = read_csv(RESULTS_DIR / "calibration" / "pool_thresholds.csv")
    fig, ax = plt.subplots(figsize=(6.5, 2.7))
    for group, color, marker in zip(LENGTH_GROUPS, (ORANGE, BLUE, AQUA), "o^s"):
        points = [r for r in rows if r["length_group"] == group]
        xs = [float(r["threshold"]) for r in points]
        ys = [100 * int(r["flagged"]) / int(r["tested"]) for r in points]
        ax.plot(xs, ys, color=color, lw=2, marker=marker, ms=5, label=f"{group} words")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("Flagged unmarked passages (%)")
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "threshold_choice.png", dpi=220)


def false_positives() -> None:
    rows = fresh_rows()
    groups = list(LENGTH_GROUPS)
    single = [sum(score(r) > 0.55 for r in rows if r["length_group"] == g) for g in groups]
    tiered = [sum(r["flagged"] == "True" for r in rows if r["length_group"] == g) for g in groups]
    fig, ax = plt.subplots(figsize=(4.6, 2.3))
    for offset, values, color, label in ((-0.2, single, ORANGE, "Single 0.55"), (0.2, tiered, BLUE, "Length-based")):
        bars = ax.bar([i + offset for i in range(3)], values, width=0.36, color=color, label=label)
        ax.bar_label(bars, padding=2, color=INK)
    ax.set_xticks(range(3), [f"{g} words" for g in groups])
    ax.set_ylabel("Flagged out of 500")
    ax.set_ylim(0, 38)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "false_positives.png", dpi=220)


def method_comparison() -> None:
    labels = ["Flagged", "Meaning preserved", "Readable", "Usable and flagged"]
    fig, ax = plt.subplots(figsize=(6.5, 2.5))
    for offset, values, color, label in ((-0.2, WORD_SWAPS, ORANGE, "Word swaps"), (0.2, REWRITING, BLUE, "Sentence rewriting")):
        bars = ax.bar([i + offset for i in range(4)], values, width=0.36, color=color, label=label)
        ax.bar_label(bars, padding=2, color=INK)
    ax.set_xticks(range(4), labels)
    ax.set_ylabel("Passages out of 10")
    ax.set_ylim(0, 12)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    fig.tight_layout()
    fig.savefig(OUT / "method_comparison.png", dpi=220)


def watermarking() -> None:
    rows = sorted(read_csv(FIRST / "wm_scores.csv"), key=lambda r: float(r["score_after"]))
    fig, ax = plt.subplots(figsize=(6.5, 2.9))
    for y, r in enumerate(rows):
        before, after = float(r["score_before"]), float(r["score_after"])
        flagged = r["flagged_after"] == "True"
        ax.plot([before, after], [y, y], color=GRID, lw=2, zorder=1)
        ax.scatter(before, y, s=30, color=MUTED, zorder=2)
        ax.scatter(after, y, s=38, color=BLUE, edgecolor=BLUE, facecolor=BLUE if flagged else SURFACE, lw=1.4, zorder=2)
    ax.axvline(0.55, color=INK, lw=1)
    ax.text(0.552, len(rows) - 0.35, "threshold 0.55", color=INK, va="bottom")
    ax.scatter([], [], s=30, color=MUTED, label="Original")
    ax.scatter([], [], s=38, color=BLUE, label="Output, flagged")
    ax.scatter([], [], s=38, edgecolor=BLUE, facecolor=SURFACE, lw=1.4, label="Output, not flagged")
    ax.set_yticks(range(len(rows)), [r["id"] for r in rows])
    ax.set_xlabel("Green fraction")
    ax.set_xlim(0.34, 0.62)
    ax.set_ylim(-0.6, len(rows) + 0.1)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.2))
    fig.tight_layout()
    fig.savefig(OUT / "watermarking_scores.png", dpi=220)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    distribution()
    threshold_choice()
    false_positives()
    watermarking()
    method_comparison()
