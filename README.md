# Keyed Text Watermarking

Keyed word watermarking and experiment scripts. See `project-description-2026-fall.md`.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). No third-party runtime dependencies.

```sh
uv sync --group report
uv run wm keygen          # once; writes secrets/watermark.key (demonstration key)
```

## Milestone 1 pipeline

```sh
# 1. Add raw texts to data/sources/raw/ and list them in data/sources/sources.csv
uv run python scripts/collect_passages.py   # -> data/passages/candidates.jsonl
uv run python scripts/split.py              # -> data/splits/*, manifest.json (run once, before scoring)

# 2. Calibrate (repeat as needed; each run is saved separately)
uv run python scripts/run.py calibration    # -> results/calibration/run-*/
#    teammate fills review_sheet.csv blind, then:
uv run python scripts/report.py results/calibration/run-<timestamp>

# 3. Fix settings: edit config/settings.toml, set frozen = true, commit
uv run python scripts/run.py evaluation
uv run python scripts/report.py results/evaluation/run-<timestamp>

# 4. Post-evaluation design, reported separately
uv run python scripts/threshold_pool.py     # -> results/calibration/pool_thresholds.csv
PYTHONPATH=scripts uv run python scripts/run_v2.py   # -> results/post-evaluation/run-*/
uv run --group report python scripts/figures.py      # -> report/figures/
```

Sentence rewriting (separate run): `results/rewrite/PROCEDURE.md` has the rules, and `scripts/rewrite_tool.py` shows word colors and scores saved rewrites.

Use `scripts/report.py --pending <run_dir>` for a summary before usability review.
`scripts/check_watermark.py` is a self-check for the watermarking edits.

Ad hoc use:

```sh
uv run wm score passage.txt
uv run wm watermark passage.txt > out.txt
```

## Word processing

Implemented in `src/wmark/text.py` and used for both watermarking and detection.

| Step | Rule |
| --- | --- |
| Unicode | NFKC normalization |
| Apostrophes | `’ ‘ ʼ ＇` become `'` |
| Format characters | Unicode category Cf (zero-width space/joiner, soft hyphen, BOM) removed before tokenizing |
| Words | Runs of letters, optionally joined by internal apostrophes (`don't`). Digits, punctuation, hyphens, and whitespace separate words |
| Case | Casefolded (`Book` = `book`) |

Input with no words raises `EmptyInputError`. A score equal to the threshold is unflagged (exact rational comparison).
Watermarked output is the preprocessed text (NFKC, Cf removed) with substitutions applied.

## Layout

| Path | Contents |
| --- | --- |
| `src/wmark/` | Detector, color function, word processing, watermarking |
| `scripts/` | Experiment pipeline |
| `config/settings.toml` | Frozen settings for the first evaluation |
| `config/settings_v2.toml` | Length-based thresholds for the post-evaluation run |
| `config/settings_v3.toml` | The same thresholds, used for the sentence rewriting run |
| `data/sources/` | Raw source texts and `sources.csv` |
| `data/splits/` | Calibration/evaluation sets and `manifest.json` |
| `data/synonyms.json` | Hand-built synonym list; order is the edit order |
| `results/` | Saved runs, one directory per run; `results/proxy-review/` and `results/rewrite/review-*` hold AI proxy quality reviews; `results/rewrite/` holds sentence rewrites |
| `report/` | Milestone reports; PNG charts in `report/figures/` |
| `secrets/` | Demonstration watermark key |

## Data sources

46 Project Gutenberg books. Sources: `data/sources/sources.csv`. Split assignments: `data/splits/manifest.json`.

| Source ID | Title | Author | URL | License |
| --- | --- | --- | --- | --- |
| 1342 | Pride and Prejudice | Jane Austen | https://www.gutenberg.org/cache/epub/1342/pg1342.txt | Project Gutenberg License; public domain in the U.S. |
| 84 | Frankenstein | Mary Shelley | https://www.gutenberg.org/cache/epub/84/pg84.txt | Project Gutenberg License; public domain in the U.S. |
| 2701 | Moby-Dick | Herman Melville | https://www.gutenberg.org/cache/epub/2701/pg2701.txt | Project Gutenberg License; public domain in the U.S. |
| 11 | Alice’s Adventures in Wonderland | Lewis Carroll | https://www.gutenberg.org/cache/epub/11/pg11.txt | Project Gutenberg License; public domain in the U.S. |
| 1661 | The Adventures of Sherlock Holmes | Arthur Conan Doyle | https://www.gutenberg.org/cache/epub/1661/pg1661.txt | Project Gutenberg License; public domain in the U.S. |
| 345 | Dracula | Bram Stoker | https://www.gutenberg.org/cache/epub/345/pg345.txt | Project Gutenberg License; public domain in the U.S. |
| 145 | Middlemarch | George Eliot | https://www.gutenberg.org/cache/epub/145/pg145.txt | Project Gutenberg License; public domain in the U.S. |
| 174 | The Picture of Dorian Gray | Oscar Wilde | https://www.gutenberg.org/cache/epub/174/pg174.txt | Project Gutenberg License; public domain in the U.S. |
| 43 | The Strange Case of Dr. Jekyll and Mr. Hyde | Robert Louis Stevenson | https://www.gutenberg.org/cache/epub/43/pg43.txt | Project Gutenberg License; public domain in the U.S. |
| 1260 | Jane Eyre | Charlotte Brontë | https://www.gutenberg.org/cache/epub/1260/pg1260.txt | Project Gutenberg License; public domain in the U.S. |
| 2554 | Crime and Punishment | Fyodor Dostoevsky | https://www.gutenberg.org/cache/epub/2554/pg2554.txt | Project Gutenberg License; public domain in the U.S. |
| 64317 | The Great Gatsby | F. Scott Fitzgerald | https://www.gutenberg.org/cache/epub/64317/pg64317.txt | Project Gutenberg License; public domain in the U.S. |
| 5200 | The Metamorphosis | Franz Kafka | https://www.gutenberg.org/cache/epub/5200/pg5200.txt | Project Gutenberg License; public domain in the U.S. |
| 1184 | The Count of Monte Cristo | Alexandre Dumas | https://www.gutenberg.org/cache/epub/1184/pg1184.txt | Project Gutenberg License; public domain in the U.S. |
| 1400 | Great Expectations | Charles Dickens | https://www.gutenberg.org/cache/epub/1400/pg1400.txt | Project Gutenberg License; public domain in the U.S. |
| 514 | Little Women | Louisa May Alcott | https://www.gutenberg.org/cache/epub/514/pg514.txt | Project Gutenberg License; public domain in the U.S. |
| 74 | The Adventures of Tom Sawyer | Mark Twain | https://www.gutenberg.org/cache/epub/74/pg74.txt | Project Gutenberg License; public domain in the U.S. |
| 2600 | War and Peace | Leo Tolstoy | https://www.gutenberg.org/cache/epub/2600/pg2600.txt | Project Gutenberg License; public domain in the U.S. |
| 768 | Wuthering Heights | Emily Brontë | https://www.gutenberg.org/cache/epub/768/pg768.txt | Project Gutenberg License; public domain in the U.S. |
| 33 | The Scarlet Letter | Nathaniel Hawthorne | https://www.gutenberg.org/cache/epub/33/pg33.txt | Project Gutenberg License; public domain in the U.S. |
| 46 | A Christmas Carol | Charles Dickens | https://www.gutenberg.org/cache/epub/46/pg46.txt | Project Gutenberg License; public domain in the U.S. |
| 76 | Adventures of Huckleberry Finn | Mark Twain | https://www.gutenberg.org/cache/epub/76/pg76.txt | Project Gutenberg License; public domain in the U.S. |
| 35 | The Time Machine | H. G. Wells | https://www.gutenberg.org/cache/epub/35/pg35.txt | Project Gutenberg License; public domain in the U.S. |
| 120 | Treasure Island | Robert Louis Stevenson | https://www.gutenberg.org/cache/epub/120/pg120.txt | Project Gutenberg License; public domain in the U.S. |
| 45 | Anne of Green Gables | L. M. Montgomery | https://www.gutenberg.org/cache/epub/45/pg45.txt | Project Gutenberg License; public domain in the U.S. |
| 55 | The Wonderful Wizard of Oz | L. Frank Baum | https://www.gutenberg.org/cache/epub/55/pg55.txt | Project Gutenberg License; public domain in the U.S. |
| 205 | Walden | Henry David Thoreau | https://www.gutenberg.org/cache/epub/205/pg205.txt | Project Gutenberg License; public domain in the U.S. |
| 23 | Narrative of the Life of Frederick Douglass | Frederick Douglass | https://www.gutenberg.org/cache/epub/23/pg23.txt | Project Gutenberg License; public domain in the U.S. |
| 1080 | A Modest Proposal | Jonathan Swift | https://www.gutenberg.org/cache/epub/1080/pg1080.txt | Project Gutenberg License; public domain in the U.S. |
| 1952 | The Yellow Wallpaper | Charlotte Perkins Gilman | https://www.gutenberg.org/cache/epub/1952/pg1952.txt | Project Gutenberg License; public domain in the U.S. |
| S05 | A Tale of Two Cities | Charles Dickens | https://www.gutenberg.org/cache/epub/98/pg98.txt | Public domain in the USA (Project Gutenberg) |
| S10 | Heart of Darkness | Joseph Conrad | https://www.gutenberg.org/cache/epub/219/pg219.txt | Public domain in the USA (Project Gutenberg) |
| S11 | The War of the Worlds | H. G. Wells | https://www.gutenberg.org/cache/epub/36/pg36.txt | Public domain in the USA (Project Gutenberg) |
| S18 | Up from Slavery: An Autobiography | Booker T. Washington | https://www.gutenberg.org/cache/epub/2376/pg2376.txt | Public domain in the USA (Project Gutenberg) |
| S19 | The Voyage of the Beagle | Charles Darwin | https://www.gutenberg.org/cache/epub/944/pg944.txt | Public domain in the USA (Project Gutenberg) |
| S20 | On the Origin of Species | Charles Darwin | https://www.gutenberg.org/cache/epub/2009/pg2009.txt | Public domain in the USA (Project Gutenberg) |
| S21 | Life on the Mississippi | Mark Twain | https://www.gutenberg.org/cache/epub/245/pg245.txt | Public domain in the USA (Project Gutenberg) |
| S22 | An Inquiry into the Nature and Causes of the Wealth of Nations | Adam Smith | https://www.gutenberg.org/cache/epub/3300/pg3300.txt | Public domain in the USA (Project Gutenberg) |
| S23 | On Liberty | John Stuart Mill | https://www.gutenberg.org/cache/epub/34901/pg34901.txt | Public domain in the USA (Project Gutenberg) |
| S24 | Second Treatise of Government | John Locke | https://www.gutenberg.org/cache/epub/7370/pg7370.txt | Public domain in the USA (Project Gutenberg) |
| S25 | The Problems of Philosophy | Bertrand Russell | https://www.gutenberg.org/cache/epub/5827/pg5827.txt | Public domain in the USA (Project Gutenberg) |
| S26 | Meditations | Marcus Aurelius (tr. Meric Casaubon) | https://www.gutenberg.org/cache/epub/2680/pg2680.txt | Public domain in the USA (Project Gutenberg) |
| S27 | Essays: First Series | Ralph Waldo Emerson | https://www.gutenberg.org/cache/epub/2944/pg2944.txt | Public domain in the USA (Project Gutenberg) |
| S28 | The Federalist Papers | Alexander Hamilton, John Jay, James Madison | https://www.gutenberg.org/cache/epub/18/pg18.txt | Public domain in the USA (Project Gutenberg) |
| S29 | Common Sense | Thomas Paine | https://www.gutenberg.org/cache/epub/147/pg147.txt | Public domain in the USA (Project Gutenberg) |
| S30 | The Prince | Niccolò Machiavelli (tr. W. K. Marriott) | https://www.gutenberg.org/cache/epub/1232/pg1232.txt | Public domain in the USA (Project Gutenberg) |

## Contribution statement

| Member | Work | Commits |
| --- | --- | --- |
| Rowan (Goldbarn) | First source list, first split, key generation, first calibration run | [c8b9738](https://github.com/Goldbarn/DSAPprojRepo/commit/c8b9738), [260107d](https://github.com/Goldbarn/DSAPprojRepo/commit/260107d) |
| Wil N | Second source list, including the nonfiction sources | [37c28d8](https://github.com/Goldbarn/DSAPprojRepo/commit/37c28d8) |
| Austin (Yoyojesus) | Package setup, detector, watermarker, pipeline scripts, merged data, expanded synonym list, calibration and evaluation runs, figures, report drafting | [6512aea](https://github.com/Goldbarn/DSAPprojRepo/commit/6512aea), [bc2165d](https://github.com/Goldbarn/DSAPprojRepo/commit/bc2165d), [8214a75](https://github.com/Goldbarn/DSAPprojRepo/commit/8214a75), [58b4da5](https://github.com/Goldbarn/DSAPprojRepo/commit/58b4da5), [c721687](https://github.com/Goldbarn/DSAPprojRepo/commit/c721687), [7691143](https://github.com/Goldbarn/DSAPprojRepo/commit/7691143) |

Claude Code and GPT models assisted with code, data preparation, report drafting, sentence rewriting, and simplification. GPT-6.1 acted as a proxy quality reviewer, because no teammate review was completed.
