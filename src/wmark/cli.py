import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from wmark.color import generate_key, load_key
from wmark.detector import EmptyInputError, detect
from wmark.settings import KEY_PATH, SYNONYMS_PATH, load_settings
from wmark.watermark import load_synonyms, watermark


def read_input(path: str | None) -> str:
    return Path(path).read_text(encoding="utf-8") if path else sys.stdin.buffer.read().decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(prog="wm")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("keygen", help="generate the experiment key (once)")

    p_score = sub.add_parser("score", help="score a passage")
    p_score.add_argument("file", nargs="?", help="text file (default: stdin)")
    p_score.add_argument("--threshold", type=float)

    p_wm = sub.add_parser("watermark", help="watermark a passage")
    p_wm.add_argument("file", nargs="?", help="text file (default: stdin)")
    p_wm.add_argument("--target", type=float)

    args = parser.parse_args()

    if args.cmd == "keygen":
        generate_key(KEY_PATH)
        print(f"wrote {KEY_PATH}")
        return

    settings = load_settings()
    key = load_key(KEY_PATH)
    text = read_input(args.file)

    if args.cmd == "score":
        try:
            d = detect(text, key, args.threshold if args.threshold is not None else settings.threshold)
        except EmptyInputError as e:
            sys.exit(f"error: {e}")
        print(json.dumps(asdict(d) | {"green_fraction": d.green_fraction}, indent=2))
    elif args.cmd == "watermark":
        r = watermark(
            text,
            key,
            load_synonyms(SYNONYMS_PATH),
            target=args.target if args.target is not None else settings.target,
            max_seconds=settings.max_seconds,
            max_substitutions=settings.max_substitutions,
        )
        print(r.text)
        print(
            json.dumps({k: v for k, v in asdict(r).items() if k != "text"}, indent=2),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
