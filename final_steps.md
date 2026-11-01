# Final steps for Milestone 1

[PR #1](https://github.com/Goldbarn/DSAPprojRepo/pull/1) has merged into `main`. The new charts and 100-passage
rewriting test are on `feat/large-rewrite-test`. These steps remain before submission.

**The additional charts and 100-passage run, including their follow-up quality review, can be left until after
Milestone 1. They are optional follow-up work, not a prerequisite for submitting Milestone 1.** The original
Milestone 1 report and required teammate review still need to be finished.

## 1. Trim the report

- File: `report/milestone1.md`
- It has about 4,030 words plus figures and tables. The limit is 6 pages, not counting references or the contribution statement.
- Merge Sections 4.5, 4.6, and 4.7 into one short post-evaluation section, then shorten the threat table in Section 5.
- Keep the original results in Section 4.1 as they are. The project requires them to stay.
- Figures are in `report/figures/`, with captions in `report/figures/README.md`.
- The additional charts are optional assets, not extra pages to append to the report. Keep the 100-passage
  detection results separate from usable-success results until quality review is complete.

## 2. Get a teammate to review the rewrites

The project requires a teammate review. The saved quality results are proxy reviews; the teammate review is still outstanding.

- Who: Will or Rowen, who did not edit these passages.
- Compare each file in `results/rewrite/evaluation/original/` with the same file name in `results/rewrite/evaluation/watermarked/`.
- Answer yes or no: Is the main meaning preserved? Is the prose readable?
- Do not open `results/rewrite/evaluation/wm_scores.csv` or anything else with scores until the answers are recorded.
- Save the answers in a new file, `results/rewrite/teammate_review.csv`, with these columns: `id,reviewer,meaning_preserved,readable,notes`.
- Update the table in Section 4.6 of the report and name the reviewer.

If nobody can review, ask the instructor whether the existing proxy results are acceptable. Keep them labeled as proxy results.

For the separate 100-passage run:

- Send only `results/rewrite/large-test/review_pairs.md` and `results/rewrite/large-test/review_sheet.csv`
  to a teammate who did not edit the passages. They fill both yes/no quality answers and their name.
- Keep `results/rewrite/large-test/review_key.csv`, `wm_scores.csv`, and `summary.md` hidden until answers are recorded.
- After review, join labels to IDs with `review_key.csv` and count outputs that pass both quality questions
  and are flagged. Use all 100 attempts as the denominator. Do not change the frozen rewrites.
- Add the quality results to a separate report section if using this run in the submission. Explain the three-editor
  setup, previously scored source pool, correlated passages within books, and incomplete early timing measurements.
- This entire 100-passage review and report update can wait until after Milestone 1.

## 3. Check the contribution statement

- File: `README.md`, under `## Contribution statement`
- Confirm that each person's work is described correctly.

## 4. Export and submit

- Export `report/milestone1.md` to the format the course wants, and check the page count and that the figures appear.
- Submit the report and the repository link.

## After Milestone 1

- Review and merge the optional PR from `feat/large-rewrite-test` when ready; PR #1 is already merged.

The 100-passage test protocol is in `results/rewrite/LARGE_TEST.md`. Detection results are in
`results/rewrite/large-test/summary.md`; usable success remains pending teammate review. Do not use newly
flagged passages as verified usable attack inputs before that review.

Milestone 2 starts from the 4 usable and flagged rewrites: `1184-1511`, `2600-1571`, `345-0233`, and `84-0017`, in `results/rewrite/evaluation/watermarked/`. The 6 usable passages from the broader test are in `results/rewrite/fresh/watermarked/`. Report any use of those 6 separately.
