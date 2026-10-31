# Rewriting procedure (v3)

Fixed from calibration before any evaluation passage was opened. An editor with the key rewrites each passage at the
sentence level, using `scripts/rewrite_tool.py` to see word colors and the live score.

1. Target a green fraction of at least 0.57 (detection threshold 0.56 for passages of 100 or more words).
2. Keep every sentence's claim, its facts, and the passage's voice, period, and dialect.
3. Prefer restructuring: split sentences to drop `and`, use possessives or plurals in place of `the`, and choose
   natural green words. Never make a swap that breaks grammar.
4. Keep distinctive original phrasing and idioms unless the target needs the change.
5. Do not repeat a device such as `then` or `that` often enough for a reader to notice.
6. Once above the target, give margin back by restoring original wording.
7. Stop at the target or after 15 minutes per passage, and keep the best output even if it misses.

## Revision for the broader test

Added after the evaluation review, before any passage in `data/splits/fresh_wm.jsonl` was opened. These rules use
information from the 10 evaluation passages, so they are tested only on new passages.

8. Read the finished text as a stranger would. Every changed phrase must be something a writer of that period would
   plausibly write. Odd constructions such as `his throat held by a wolf` or `of tiny feet` do not pass.
9. Keep verbs of thought and speech as the original has them. `he felt, "They have come back!"` does not pass.
10. Use `some` only where it is natural, and do not replace a person's name or noun with `that fellow` repeatedly.
11. Do not use `that` as a loose relative after a comma, and do not cut a sentence so far that it loses its grammar.
12. Stop once the passage is flagged if the next edit would cost readability. Quality outranks the 0.57 target, and a
    passage that cannot be flagged cleanly is kept as a miss.

