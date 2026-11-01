"""Additional charts from saved results. Run: uv run --group report python scripts/rewrite_figures.py."""

import json

from figures import AQUA, BLUE, GRID, INK, MUTED, ORANGE, OUT, SURFACE, plt

from wmark.records import read_csv, write_csv
from wmark.settings import RESULTS_DIR


def rewriting_outcomes() -> None:
    review_dir = RESULTS_DIR / "rewrite" / "review-3"
    key = json.loads((review_dir / "key.json").read_text(encoding="utf-8"))
    reviews = {key[r["label"]]: r for r in read_csv(review_dir / "answers.csv")}
    rows = read_csv(RESULTS_DIR / "rewrite" / "fresh" / "wm_scores.csv")
    assert len(rows) == len(reviews) == 20
    assert {r["id"] for r in rows} == set(reviews)
    categories = ["Usable and flagged", "Quality passed, not flagged", "Flagged, quality failed", "Neither"]
    colors = [AQUA, BLUE, ORANGE, MUTED]
    joined = []
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for r in rows:
        review = reviews[r["id"]]
        quality = review["meaning_preserved"] == "yes" and review["readable"] == "yes"
        flagged = r["flagged_after"] == "True"
        category = 0 if quality and flagged else 1 if quality else 2 if flagged else 3
        before, after = float(r["score_before"]), float(r["score_after"])
        changes = int(r["changed_words"])
        axes[0].scatter(before, after, color=colors[category], s=45, edgecolor=SURFACE)
        axes[1].scatter(changes, after - before, color=colors[category], s=45, edgecolor=SURFACE)
        joined.append({**r, "meaning_preserved": review["meaning_preserved"], "readable": review["readable"],
                       "outcome": categories[category]})
    for label, color in zip(categories, colors):
        count = sum(r["outcome"] == label for r in joined)
        axes[0].scatter([], [], color=color, label=f"{label} ({count})")
    axes[0].plot([0.3, 0.65], [0.3, 0.65], color=GRID, ls=":", label="No score change")
    axes[0].axhline(0.56, color=INK, lw=1, ls="--")
    axes[0].text(0.305, 0.565, "Detection threshold 0.56", fontsize=8)
    axes[0].set(xlabel="Original green fraction", ylabel="Rewritten green fraction", xlim=(0.3, 0.65), ylim=(0.3, 0.65))
    axes[1].axhline(0, color=GRID, ls=":")
    axes[1].set(xlabel="Changed words (diff count)", ylabel="Green fraction increase")
    for ax in axes:
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False, fontsize=8)
    fig.suptitle("Fresh rewriting test: 20 passages, proxy quality review", fontsize=11)
    fig.tight_layout(rect=(0, 0.18, 1, 0.95))
    fig.savefig(OUT / "rewrite_outcomes.png", dpi=220)
    plt.close(fig)
    write_csv(OUT / "rewrite_outcomes.csv", joined)


def full_pool_false_positives() -> None:
    rows = read_csv(RESULTS_DIR / "backtest" / "unmarked_thresholds.csv")
    assert sum(int(r["tested"]) for r in rows) == 19558
    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    for offset, field, color, label in (
        (-0.2, "flagged_single_055", ORANGE, "Single threshold 0.55"),
        (0.2, "flagged_length_based", BLUE, "Length-based thresholds"),
    ):
        rates = [100 * int(r[field]) / int(r["tested"]) for r in rows]
        bars = ax.bar([i + offset for i in range(len(rows))], rates, width=0.36, color=color, label=label)
        ax.bar_label(
            bars, labels=[f"{v:.2f}%\n{r[field]}/{r['tested']}" for v, r in zip(rates, rows)], fontsize=8, padding=3
        )
    ax.set_xticks(range(len(rows)), [f"{r['length_group']} words" for r in rows])
    ax.set(ylabel="Unmarked passages flagged (%)", ylim=(0, 6.2))
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Remaining evaluation-source pool: 19,558 passages", loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "full_pool_false_positives.png", dpi=220)
    plt.close(fig)


def large_rewrite() -> None:
    rows = read_csv(RESULTS_DIR / "rewrite" / "large-test" / "wm_scores.csv")
    assert len(rows) == 100 and len({r["id"] for r in rows}) == 100
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for flag, color, label in [("True", BLUE, "Flagged"), ("False", ORANGE, "Not flagged")]:
        group = [r for r in rows if r["flagged_after"] == flag]
        axes[0].scatter([float(r["score_before"]) for r in group], [float(r["score_after"]) for r in group],
                        color=color, s=28, alpha=0.75, label=f"{label} ({len(group)})")
        axes[1].scatter([int(r["changed_words"]) for r in group],
                        [float(r["score_after"]) - float(r["score_before"]) for r in group],
                        color=color, s=28, alpha=0.75)
    lower = min(float(r["score_before"]) for r in rows) - 0.02
    upper = max(float(r["score_after"]) for r in rows) + 0.03
    thresholds = sorted({float(r["threshold_after"]) for r in rows})
    upper = max(upper, max(thresholds) + 0.03)
    axes[0].plot([lower, upper], [lower, upper], color=GRID, ls=":")
    for threshold in thresholds:
        axes[0].axhline(threshold, color=INK, ls="--", lw=1)
        length = "100+ words" if threshold == 0.56 else "under 100 words"
        axes[0].text(lower + 0.005, threshold + 0.005, f"{threshold:.2f} ({length})", fontsize=8)
    axes[0].set(xlabel="Original green fraction", ylabel="Rewritten green fraction",
                xlim=(lower, upper), ylim=(lower, upper))
    axes[1].axhline(0, color=GRID, ls=":")
    axes[1].set(xlabel="Changed words (diff count)", ylabel="Green fraction increase")
    for ax in axes:
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False)
    fig.suptitle("100-passage rewriting run: detection only, quality review pending", fontsize=11)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(OUT / "large_rewrite_detection.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rewriting_outcomes()
    full_pool_false_positives()
    if (RESULTS_DIR / "rewrite" / "large-test" / "wm_scores.csv").exists():
        large_rewrite()
