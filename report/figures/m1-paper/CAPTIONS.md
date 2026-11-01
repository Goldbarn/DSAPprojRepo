# Milestone 1 PNG assets

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
