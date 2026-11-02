# Final steps for Milestone 1

[PR #1](https://github.com/Goldbarn/DSAPprojRepo/pull/1) has merged into `main`. The code, data, runs, figures, and report are in `main`. The report we submit is `report/MS1report.pdf`, built from `report/MS1report.md`.

## 1. Human review (done)

Will Nahra reviewed all 20 outputs. The answers are in `results/human-review/review_answers.csv`, the returned sheet is `results/human-review/review_sheet_completed.md`, and `results/human-review/key.json` decodes the labels. Word swaps: 0 of 10 usable. Rewrites: 10 of 10 usable. The results are in the report and in Table 3.

Will also reviewed the 5 calibration outputs after the evaluation: 0 of 5 usable. The answers are in `results/human-review/calibration_answers.csv`, and the returned sheet is `results/human-review/calibration_sheet_completed.md`.

## 2. Check the contribution statement

- File: `README.md`, under `## Contribution statement`
- Confirm that each person's work is described correctly.

## 3. Export and submit

- The limit is 6 pages, not counting references or the contribution statement.
- Rebuild `report/MS1report.pdf` after any edit to `report/MS1report.md` with `typst compile report/MS1report.typ`, then check that it is still 6 pages.
- Give the course staff access to the repository, which is private, because the spec requires the code and README.
- Submit `report/MS1report.pdf` and the repository link.

## After Milestone 1

Milestone 2 starts from the 8 usable and flagged rewrites: `S05-0533`, `1400-0614`, `2554-0062`, `84-0017`, `2600-1571`, `345-0233`, `2600-2189`, and `514-0605`, in `results/rewrite/evaluation/watermarked/`. The rewrites in `results/rewrite/fresh/watermarked/` have no human review.
