# Report figures

Regenerate with `uv run --group report python scripts/figures.py` (run `scripts/threshold_pool.py` first if the pool CSV is missing).

| File | Suggested caption |
| --- | --- |
| `score_distribution.png` | Green fractions of 1,500 fresh unmarked passages by length group. Short passages spread much wider, so one threshold cannot suit all lengths. |
| `threshold_choice.png` | Flagged share of 1,933 calibration-source passages at each threshold. Nearly all false positives above 0.56 are under 100 words. |
| `false_positives.png` | False positives on 1,500 fresh passages under the original threshold and the length-based thresholds. |
| `watermarking_scores.png` | Scores before and after watermarking for the 10 evaluation passages at threshold 0.55. Hollow markers were not flagged. |
