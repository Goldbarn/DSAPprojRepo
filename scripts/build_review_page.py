"""Build the blind teammate review page: results/human-review/review.html, plus key.json to decode its labels.

Send only review.html to the reviewer. It holds no passage IDs, scores, decisions, or method names.
"""

import json
import random

from wmark.records import read_jsonl
from wmark.settings import RESULTS_DIR, ROOT, SPLITS_DIR

OUT = RESULTS_DIR / "human-review"
TEMPLATE = ROOT / "scripts" / "review_page.html"
CALIBRATION = RESULTS_DIR / "calibration" / "run-20261031-123747" / "watermarked"
METHODS = {
    "word_swaps": RESULTS_DIR / "evaluation" / "run-20261031-124055" / "watermarked",
    "rewriting": RESULTS_DIR / "rewrite" / "evaluation" / "watermarked",
}


def main() -> None:
    passages = read_jsonl(SPLITS_DIR / "evaluation_wm.jsonl")
    pairs = [(method, p) for method in METHODS for p in passages]
    random.Random(1101).shuffle(pairs)
    items, key = [], {}
    for n, (method, p) in enumerate(pairs, 1):
        label = f"R{n:02d}"
        key[label] = {"method": method, "id": p["id"]}
        edited = (METHODS[method] / f"{p['id']}.txt").read_text(encoding="utf-8").strip()
        items.append({"label": label, "original": p["text"], "edited": edited})
    OUT.mkdir(exist_ok=True)
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    (OUT / "review.html").write_text(TEMPLATE.read_text(encoding="utf-8").replace("__ITEMS__", data), encoding="utf-8")
    (OUT / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    (OUT / "review_sheet.md").write_text(review_sheet(items), encoding="utf-8")
    calibration_sheet()


def calibration_sheet() -> None:
    passages = read_jsonl(SPLITS_DIR / "calibration_wm.jsonl")
    random.Random(1101).shuffle(passages)
    items, key = [], {}
    for n, p in enumerate(passages, 1):
        label = f"C{n:02d}"
        key[label] = {"method": "word_swaps", "id": p["id"]}
        edited = (CALIBRATION / f"{p['id']}.txt").read_text(encoding="utf-8").strip()
        items.append({"label": label, "original": p["text"], "edited": edited})
    (OUT / "calibration_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    (OUT / "calibration_sheet.md").write_text(review_sheet(items), encoding="utf-8")


def quote(text: str) -> str:
    return "\n".join(f"> {line}".rstrip() for line in text.splitlines())


def review_sheet(items: list[dict]) -> str:
    lines = [
        "# Passage quality review",
        "",
        "**Reviewer name:** ",
        "",
        "Read each original and its edited version, then type `yes` or `no` after both questions.",
        "",
        "- **Meaning:** is the main meaning of the original preserved?",
        "- **Readable:** is the edited version readable prose? Allow for the period style and any dialect in the original.",
        "",
        "Judge each passage on its own. Some originals appear twice with different edits.",
        "Please do not look up scores or other project results until you have finished.",
        "",
    ]
    for n, item in enumerate(items, 1):
        lines += [
            "---",
            "",
            f"## Passage {n} of {len(items)} ({item['label']})",
            "",
            "**Original**",
            "",
            quote(item["original"]),
            "",
            "**Edited**",
            "",
            quote(item["edited"]),
            "",
            "**Meaning preserved (yes/no):** ",
            "",
            "**Readable (yes/no):** ",
            "",
            "**Notes (optional):** ",
            "",
        ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
