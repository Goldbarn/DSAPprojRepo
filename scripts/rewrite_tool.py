"""Key-aware helper for sentence-level rewriting.

  show FILE...      print the score and each text with red words in [brackets]
  words WORD...     print the color of each word
  score DIR SPLIT   write wm_scores.csv for DIR/watermarked/*.txt against data/splits/SPLIT_wm.jsonl
"""

import argparse
from pathlib import Path

from wmark.color import GREEN, load_key, word_color
from wmark.detector import detect
from wmark.records import read_jsonl, write_csv
from wmark.settings import KEY_PATH, ROOT, SPLITS_DIR, Settings, load_settings
from wmark.text import changed_words, iter_word_matches, normalize, preprocess, words

SETTINGS_V3 = ROOT / "config" / "settings_v3.toml"


def show(path: Path, key: bytes, settings: Settings) -> None:
    text = preprocess(path.read_text(encoding="utf-8"))
    d = detect(text, key, settings.threshold_for(len(words(text))))
    out, end = [], 0
    for m in iter_word_matches(text):
        out.append(text[end : m.start()])
        red = word_color(normalize(m.group()), key) != GREEN
        out.append(f"[{m.group()}]" if red else m.group())
        end = m.end()
    print(f"--- {path.name} {d.green}/{d.total} = {d.green_fraction:.3f} flagged={d.flagged}")
    print("".join(out) + text[end:])


def score(run_dir: Path, split: str, key: bytes, settings: Settings) -> None:
    rows = []
    for p in read_jsonl(SPLITS_DIR / f"{split}_wm.jsonl"):
        edited = (run_dir / "watermarked" / f"{p['id']}.txt").read_text(encoding="utf-8")
        # Each text gets the threshold for its own length: a detector never sees the original.
        before = detect(p["text"], key, settings.threshold_for(len(words(p["text"]))))
        after = detect(edited, key, settings.threshold_for(len(words(edited))))
        rows.append(
            {
                "id": p["id"],
                "source_id": p["source_id"],
                "total": after.total,
                "distinct_before": before.distinct,
                "distinct_after": after.distinct,
                "score_before": f"{before.green_fraction:.6f}",
                "flagged_before": before.flagged,
                "green_after": after.green,
                "score_after": f"{after.green_fraction:.6f}",
                "flagged_after": after.flagged,
                "reached_target": after.green_fraction >= settings.target,
                "changed_words": changed_words(p["text"], edited),
            }
        )
    write_csv(run_dir / "wm_scores.csv", rows)
    for r in rows:
        print(r["id"], r["score_before"], "->", r["score_after"], r["flagged_after"], r["changed_words"])


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show").add_argument("files", nargs="+", type=Path)
    sub.add_parser("words").add_argument("words", nargs="+")
    p_score = sub.add_parser("score")
    p_score.add_argument("run_dir", type=Path)
    p_score.add_argument("split", choices=["calibration", "evaluation", "fresh"])
    args = parser.parse_args()

    key = load_key(KEY_PATH)
    settings = load_settings(SETTINGS_V3)
    if args.cmd == "show":
        for path in args.files:
            show(path, key, settings)
    elif args.cmd == "words":
        for w in args.words:
            print(w, "green" if all(word_color(x, key) == GREEN for x in words(w)) else "red")
    else:
        score(args.run_dir, args.split, key, settings)


if __name__ == "__main__":
    main()
