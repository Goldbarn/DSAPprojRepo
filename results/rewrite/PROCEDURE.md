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
