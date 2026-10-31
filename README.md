# Keyed Text Watermarking

Word-based keyed watermarking, detection, attacks, and deployment policy. See `project-description-2026-fall.md`.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). No third-party runtime dependencies.

```sh
uv sync
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
```

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
| `config/settings.toml` | Threshold, watermarking target, stopping rule, seed |
| `data/sources/` | Raw source texts and `sources.csv` |
| `data/splits/` | Calibration/evaluation sets and `manifest.json` |
| `data/synonyms.json` | Hand-built synonym list |
| `results/` | Saved runs, one directory per run |
| `report/` | Milestone reports |
| `secrets/` | Demonstration watermark key |

## Data sources

| Source ID | Title | Author | URL | License |
| --- | --- | --- | --- | --- |
| | | | | |

## Contribution statement

| Member | Work | Commits |
| --- | --- | --- |
| | | |
