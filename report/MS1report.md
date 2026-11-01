Milestone 1 Report
============

Rowan Ess, Austin Sternberg, Wil Nahra

---

Introduction
------------

As artificial intelligence (AI) has come to dominate more and more of the technology-focused world, many issues have arisen with both dishonesty and honestly mistaking large language models (LLM)'s output for the creations of a human hand. This is an issue in many fields, for academics, for journalism, for literature, for the visual arts, for music, and for all areas of computer science. There are a few methods that have been devised to detect when some product is the spawn of machine rather than man, and of those, watermarking is the current preeminent method for the examination of bodies of text. 

In this report, we will endeavour to explain the implimentation and results of a method of watermarking that "colors" words in such a way that if a threshold of those colored words is reached, the text is flagged. This is, of course, calibrated such that it will preferably give no false positives, though that is a difficult thing to gurantee.

Implimentation
------------

The basic function of the program is fairly simple, starting with generating a 32-byte long key. This key is then used to hash each word, and the last bit of the hash determines whether it is considered a "red" word (0) or a "green" word (1). The document is scored on number of green words divided by number of reds, and is flagged when the score is greater than the threshold.

The data used for this program's calibration and evaluation were collected from Project Gutenburg. 46 books were collected, totalling 23,171 viable passages, though only 315 were used.

For calibration, we ran the 150 calibration prose passages through the red/green program, and then filtered out the thresholds that would have given false positives:

| Threshold | Flagged unmarked | Unflagged outputs |
| ---: | ---: | ---: |
| 0.50 | 4 of 150 | 0 of 5 |
| 0.55 | 0 of 150 | 1 of 5 |
| 0.60 | 0 of 150 | 5 of 5 |
| 0.65 | 0 of 150 | 5 of 5 |

We chose 0.55, which had no false positives in this test, and flagged 4/5 of the marked ones. 80% accuracy with negligible false positives was considered sufficient for the purposes of this program.

Evaluation
------------

The results of our evaluation step (with 150 unmarked and 10 marked) were as thus:

| Measurement | Result |
| --- | --- |
| Unmarked false-positive rate | 3 / 150 = 2.0% |
| Detection rate on watermarking outputs | 7 / 10 = 70% |
| Usable watermarking success rate | 0 / 10 = 0% |

To explain, the false positives being only 2% is good, considering 

![Scores before and after watermarking](figures/watermarking_scores.png)

<4.2 teammate qual check one paragraph>

<4.4 false flags one paragraph>

<4.5/6/7 later tests idk paragraphs>


References
------------

- J. Kirchenbauer, J. Geiping, Y. Wen, J. Katz, I. Miers, and T. Goldstein. A Watermark for Large Language Models. ICML 2023. https://arxiv.org/abs/2301.10226
- Project Gutenberg texts, listed with URLs and licenses in `README.md` and `data/sources/sources.csv`.
