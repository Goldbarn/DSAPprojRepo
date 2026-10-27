"""Extract candidate passages from raw source texts listed in data/sources/sources.csv.

Passages are runs of consecutive paragraphs whose normalized word count lands in a length group.
Windows never overlap, and duplicate passages (same normalized words) are dropped.
"""

import hashlib
import re

from wmark.records import LENGTH_GROUPS, length_group, read_csv, write_jsonl
from wmark.settings import CANDIDATES_PATH, RAW_DIR, SOURCES_CSV
from wmark.text import words

GUTENBERG_START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
GUTENBERG_END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", re.I)
MIN_PARAGRAPH_WORDS = 8


def strip_boilerplate(text: str) -> str:
    if m := GUTENBERG_START.search(text):
        text = text[m.end() :]
    if m := GUTENBERG_END.search(text):
        text = text[: m.start()]
    return text


def paragraphs(text: str) -> list[str]:
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text)]
    # Drop headings, chapter titles, and other fragments.
    return [p for p in paras if len(words(p)) >= MIN_PARAGRAPH_WORDS and not p.isupper()]


def windows(paras: list[str]):
    groups = list(LENGTH_GROUPS.values())
    k, i = 0, 0
    while i < len(paras):
        lo, hi = groups[k % len(groups)]
        chunk, n, j = [], 0, i
        while j < len(paras) and n < lo:
            chunk.append(paras[j])
            n += len(words(paras[j]))
            j += 1
        if lo <= n <= hi:
            yield "\n\n".join(chunk), n
            k += 1
            i = j
        else:
            i += 1


def main() -> None:
    rows, seen = [], set()
    for src in read_csv(SOURCES_CSV):
        text = strip_boilerplate((RAW_DIR / src["file"]).read_text(encoding="utf-8"))
        count = 0
        for passage, n in windows(paragraphs(text)):
            toks = words(passage)
            digest = hashlib.sha256(" ".join(toks).encode()).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            count += 1
            rows.append(
                {
                    "id": f"{src['source_id']}-{count:04d}",
                    "source_id": src["source_id"],
                    "n_words": n,
                    "n_distinct": len(set(toks)),
                    "length_group": length_group(n),
                    "text": passage,
                }
            )
        print(f"{src['source_id']}: {count} candidates")
    write_jsonl(CANDIDATES_PATH, rows)
    print(f"wrote {len(rows)} candidates to {CANDIDATES_PATH}")


if __name__ == "__main__":
    main()
