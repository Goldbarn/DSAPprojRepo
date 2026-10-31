# Final steps for Milestone 1

[PR #1](https://github.com/Goldbarn/DSAPprojRepo/pull/1) has merged into `main`. The code, data, runs, figures, and report draft are in `main`. These steps remain before submission.

## 1. Trim the report

- File: `report/milestone1.md`
- It has about 4,030 words plus figures and tables. The limit is 6 pages, not counting references or the contribution statement.
- Merge Sections 4.5, 4.6, and 4.7 into one short post-evaluation section, then shorten the threat table in Section 5.
- Keep the original results in Section 4.1 as they are. The project requires them to stay.
- Figures are in `report/figures/`, with captions in `report/figures/README.md`.

## 2. Get a teammate to review the rewrites

The project requires a teammate review. The saved quality results are proxy reviews; the teammate review is still outstanding.

- Who: Will or Rowen, who did not edit these passages.
- Compare each file in `results/rewrite/evaluation/original/` with the same file name in `results/rewrite/evaluation/watermarked/`.
- Answer yes or no: Is the main meaning preserved? Is the prose readable?
- Do not open `results/rewrite/evaluation/wm_scores.csv` or anything else with scores until the answers are recorded.
- Save the answers in a new file, `results/rewrite/teammate_review.csv`, with these columns: `id,reviewer,meaning_preserved,readable,notes`.
- Update the table in Section 4.6 of the report and name the reviewer.

If nobody can review, ask the instructor whether the existing proxy results are acceptable. Keep them labeled as proxy results.

## 3. Check the contribution statement

- File: `README.md`, under `## Contribution statement`
- Confirm that each person's work is described correctly.

## 4. Export and submit
- Export `report/milestone1.md` to the format the course wants, and check the page count and that the figures appear.
- Submit the report and the repository link.

## After Milestone 1

Milestone 2 starts from the 4 usable and flagged rewrites: `1184-1511`, `2600-1571`, `345-0233`, and `84-0017`, in `results/rewrite/evaluation/watermarked/`. The 6 usable passages from the broader test are in `results/rewrite/fresh/watermarked/`. Report any use of those 6 separately.
