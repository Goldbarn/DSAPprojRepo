# Frozen 100-passage rewriting test

Status: all 100 outputs are complete. Detection results are saved in `large-test/summary.md`.
Usable success remains pending until an independent teammate completes the blind quality review.

This additional experiment and its follow-up review can be left until after Milestone 1. It is not required
to finish the original Milestone 1 submission.

Run `uv run python scripts/prepare_large_rewrite.py` to create `results/rewrite/large-test/`.
The script refuses to overwrite an existing test. The manifest records the seed, input hashes, selected-passage
hash, and source counts. Selection is independent of detection scores and balances passages across available books.
Its status describes preparation; `output_manifest.json` records the later output freeze. The key hash for this
first cohort was recorded during execution and verified against the unchanged parsed key in baseline `be6a665`;
future preparations capture that hash at preparation time. Review-label mappings are also locked at output freeze.
It excludes every passage in existing split files and every calibration source. All originals have 100-199 words.
These are fresh to rewriting, but the evaluation-source pool was already scored in the false-positive back-test.
This is a larger within-corpus test, not an external validation set. Passages from the same book are correlated.

1. Use only `large-test/PROCEDURE.md` and `large-test/settings.toml`, copied at preparation time.
   Keep the existing demonstration key in `secrets/watermark.key`. Do not tune rules or thresholds during the test.
2. Rewrite every file in `large-test/original/` into `large-test/watermarked/` under the same filename.
   Use `uv run python scripts/rewrite_tool.py show PATH` and its `words` command for feedback.
   Keep the original if no acceptable rewrite is found. Include every attempt in the denominator.
   Record the editor, elapsed seconds, and stop reason in `large-test/editing_log.csv`.
   Use the existing 15-minute maximum per passage. Do not remove difficult passages or replace them.
3. Freeze all 100 outputs before quality review. Record their hashes or commit them before collecting answers.
   No edits after review. Scores alone do not establish usable watermarking success.
4. Have a separate teammate compare original and rewritten pairs in the order in `large-test/review_key.csv`.
   Prepare a reviewer-only packet labeled L001-L100 with original and rewritten text, without IDs, colors,
   scores, outcomes, or this key. The scoring command below creates that packet as `large-test/review_pairs.md`.
   The reviewer fills `large-test/review_sheet.csv` without opening scoring files or the key.
5. Score saved outputs using the frozen detector settings. Target is 0.57. Detection requires a fraction strictly
   above 0.56 for outputs of at least 100 words, or strictly above 0.68 below 100 words.
   Run `uv run python scripts/score_large_rewrite.py` after every output and batch log is complete.
   It checks the frozen cohort and rules, applies thresholds to actual output lengths, records output hashes,
   writes scores and per-book counts, and creates the blind review packet. It refuses changed frozen outputs.
6. Report flagged/100, meaning-preserved/100, readable/100, and usable-and-flagged/100 separately.
   Usable requires both quality answers to be yes and the output to be flagged. Report missing reviews as pending.
   Include changed-word counts, elapsed time, failures, source counts, and a 95% interval.
   Show results by book and account for book clustering when estimating uncertainty.

Classify text types before rewriting if testing the narrative/exposition pattern. Keep that analysis exploratory
unless the classification and comparison are frozen before outputs are inspected. Keep the earlier 20-passage
results separate. Do not pool reused passages into this test.

## Execution limits

Three parallel editor instances handle disjoint passage batches under the same frozen procedure. This differs
from the earlier single-editor run and should be disclosed when comparing results. No teammate quality answers
are filled by the editors. Early timing observations cover shared batch intervals, and some exclude initial
reading; they cannot be summed or treated as precise per-passage costs. Later observations use sequential starts.
The run summary reports detection only, with an approximate whole-book bootstrap interval to account for clustering.
