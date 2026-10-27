# Milestone 1: Detector, Evaluation, and Threat Model

Limit: 6 pages, excluding references and contribution statement.

## 1. Scheme and detector

- Key generation, word color function, scoring rule
- Word processing rules (case, punctuation, Unicode) and empty-input handling
- Generation-time watermarking (Kirchenbauer et al.) vs. word substitution

## 2. Data and split

- Sources, number of source documents, length groups
- Calibration/evaluation allocation and how sources were assigned
- Selection method for the 5 query-access forgery passages

## 3. Calibration

- Watermarking procedure, target, stopping rule
- Threshold sweep (0.55 / 0.60 / 0.65): flagged unmarked, unflagged outputs
- Chosen settings and reasoning

## 4. Evaluation

| Measurement | Result |
| --- | --- |
| Unmarked false-positive rate | |
| Detection rate on watermarking outputs | |
| Usable watermarking success rate | |

- Scores before/after, attempts reaching target, failures
- Quality check: reviewer, changed-word counting method, reviewer bias
- Length groups and repetition analysis
- Small-sample limits and shared-source correlation
- Annual false-flag estimate

## 5. Threat model

| Goal | None | Query | Key |
| --- | --- | --- | --- |
| Removal | | | |
| Forgery | | | |

Each cell: attack, expected queries and editing effort, effect on quality, defense. Label predicted vs. measured.

### Key distribution

### Context dependence

### Digital signatures

## References

## Contribution statement
