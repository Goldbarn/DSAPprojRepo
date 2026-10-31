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

The attacker is assumed to know the algorithm, the word-processing rules, and the threshold. Costs below use the calibration settings (threshold 0.55, target 0.56). **Predicted** marks an expectation not yet tested. **Measured** marks a calibration result. Milestone 2 tests query-access removal, query-access forgery, and key-access forgery.

| Goal | None | Query | Key |
| --- | --- | --- | --- |
| Removal | **Attack:** reword blindly, or undo likely edits such as `this` back to `the`. Lookalike letters (Cyrillic `а` for Latin `a`) also give a word a new, random color. **Cost:** 0 queries, about 10 to 20 word edits. **Quality:** little harm, because reversing edits restores the source wording. **Defense:** a larger margin between target and threshold, and folding lookalike characters. **Predicted:** likely success, because outputs sit 0.008 to 0.023 above the threshold and unmarked text averages 0.413 (measured). | **Attack:** swap words and keep changes that lower the score or clear the flag. **Cost:** about 2 to 3 net green-to-red swaps, so 5 to 20 queries with scores and more with binary responses. **Quality:** little harm, since few words change. **Defense:** binary responses and rate limits raise the cost but do not prevent success, because the attacker needs only one unflagged response. **Predicted:** likely success within 100 requests. | **Attack:** compute colors locally and replace green words with red synonyms. **Cost:** 0 queries needed, 1 to confirm, and 2 to 3 swaps calculated from the calibration outputs. **Quality:** little harm. **Defense:** none once the key is known, other than replacing the key. **Predicted:** near-certain success. |
| Forgery | **Attack:** apply lookalike characters to many words so that their colors are redrawn, or try synonym edits blindly. **Cost:** 0 queries, with no way to confirm the result. **Quality:** blind synonym edits harm readability, and lookalikes are invisible but machine-detectable. **Defense:** folding lookalike characters and rejecting mixed-script words. **Predicted:** low success. Blind edits move scores toward about 0.5, which is under the threshold, so most attempts should fail. | **Attack:** learn colors by submitting one word repeated, which scores 0 or 1, then edit as the watermarker does. **Cost:** 1 preparation query per word, with a 100-query budget, plus a few editing queries. The 100 most common red words cover 40.7% of calibration tokens (measured). **Quality:** similar to watermarking, and limited by which colors were learned. **Defense:** rate limits add time but not queries. Score hiding does not help, because the flag alone reveals each color. **Predicted:** success on some passages, fewer than with the key. | **Attack:** run the watermarking procedure directly. **Cost:** 0 queries, 8 to 22 edits per passage (measured). **Quality:** same as watermarking; blind review pending. **Defense:** none once the key is known, other than replacing the key. **Measured on calibration:** 4 of 5 passages flagged at 0.55. |

Word-processing rules decide which character edits matter. Case changes and zero-width characters should have no effect (**predicted**), because words are casefolded and format characters are removed before tokenizing. Inserted hyphens or digits split a word into new words, so they can change the score but are visible to a reader. NFKC does not fold Cyrillic lookalikes to Latin letters, so those edits survive normalization.

### Key distribution

The operator should hold the key and run detection as a service. Anyone who can watermark locally or detect locally holds the same key, so they can also compute colors and forge. This scheme has no public detection key, and giving the key to a partner gives them the ability to forge. Watermarking should therefore be limited to the operator's own systems, and outside parties should submit queries.

During detection the operator sees the full submitted text, so a service design has to treat submissions as sensitive even when logs omit them. An independent reviewer can check a disputed result by re-running the fixed tokenizer, key, and threshold on the disputed text in a controlled setting, ideally under an escrow arrangement so that the reviewer never takes a copy of the key. That confirms the arithmetic of the score. It cannot establish who wrote the text.

### Context dependence

If a word's color depended on preceding tokens, one repeated-word query would no longer give a color that applies everywhere. The attacker would have to learn colors for word pairs or longer contexts, which needs many more queries and makes learned colors far less reusable across passages. Query-access forgery should become much harder within a 100-query budget.

The change would not stop every attack. Editing a word would also change the color of the word after it, so each edit has a wider effect on the score, which makes legitimate watermarking harder and makes removal easier: a few scattered edits disturb several colors at once. A query attacker can still probe specific phrases from the target passage directly. Key-access attacks are unaffected, because the attacker can compute any context locally.

### Digital signatures

A digital signature binds a document to the holder of a signing key at the time of signing. Verifying it shows that this exact text was signed by that key and has not changed since. It does not show who wrote the text, only who controlled the key.

The two approaches fail differently under editing. Changing a single character invalidates a signature, while a watermark is designed to survive some edits but degrades as a passage is rewritten. A signature can also be removed by discarding it, so a missing signature proves nothing. In the same way, an unflagged watermark result proves nothing about origin.

Key compromise is also different. Signature schemes separate private signing keys from public verification keys, so anyone can verify without being able to forge, and a compromised key can be revoked with later signatures rejected. This scheme uses one shared secret for embedding and detection, so a leak allows forgery and removal and casts doubt on every earlier result. Signatures therefore give stronger evidence for text that stays unchanged. A watermark can only give a statistical signal for text with no attached metadata, and that signal has the error rates reported in Section 4.

## References

## Contribution statement
