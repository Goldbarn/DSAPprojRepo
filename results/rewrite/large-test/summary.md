# Large rewriting test: detection results

- Frozen outputs: 100 passages from 40 books.
- Flagged after rewriting: 14/100 (14%).
- Flagged before rewriting: 1/100.
- Newly flagged among initially unflagged passages: 13/99.
- Reached target 0.57: 12/100. This target alone does not imply detection for short outputs.
- Approximate 95% detection interval: 7.8% to 20.8% (10,000 whole-book bootstrap resamples).
- Median changed words: 0.
- Outputs changed: 38/100; originals retained: 62/100.
- Timing observations are in editing_log.csv. Early shared-batch intervals overlap, and some exclude initial reading. No aggregate editing-time estimate is reported.
- Meaning preservation, readability, and usable-and-flagged success: pending independent teammate review.

Send only review_pairs.md and review_sheet.csv to the reviewer. Keep review_key.csv, wm_scores.csv, and other experiment files hidden until answers are recorded.

This run uses three parallel editor instances under the same frozen rules, so it is not an exact replication of the earlier single-editor run. Editing times are wall-clock observations, not API latency benchmarks.
The passages are fresh to rewriting but drawn from an already scored pool. This within-corpus test does not establish performance on unseen books or student writing.
