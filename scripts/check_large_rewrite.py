"""Check length-aware large-test scoring. Run: uv run python scripts/check_large_rewrite.py."""

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
from io import StringIO
import json
import shutil

import score_large_rewrite
from score_large_rewrite import score_pairs

from wmark.color import GREEN, word_color
from wmark.records import read_csv, read_jsonl, write_csv
from wmark.settings import ROOT, load_settings

key = bytes(32)
green = next(w for w in ("alpha", "beta", "gamma", "delta", "theta") if word_color(w, key) == GREEN)
red = next(w for w in ("alpha", "beta", "gamma", "delta", "theta") if word_color(w, key) != GREEN)


def text(g: int, n: int) -> str:
    return " ".join([green] * g + [red] * (n - g))


settings = load_settings(ROOT / "config" / "settings_v3.toml")
with TemporaryDirectory() as temp:
    run = Path(temp)
    (run / "watermarked").mkdir()
    passages = [{"id": "short", "source_id": "a", "text": text(57, 100)},
                {"id": "equal", "source_id": "b", "text": text(57, 100)},
                {"id": "above", "source_id": "c", "text": text(56, 100)}]
    for name, edited in [("short", text(57, 99)), ("equal", text(56, 100)), ("above", text(57, 100))]:
        (run / "watermarked" / f"{name}.txt").write_text(edited, encoding="utf-8")
    rows = score_pairs(passages, run, key, settings)
    assert [r["flagged_after"] for r in rows] == [False, False, True]
    assert [r["threshold_after"] for r in rows] == [0.68, 0.56, 0.56]
    assert rows[0]["flagged_before"] is True
    assert rows[2]["reached_target"] is True
    (run / "watermarked" / "above.txt").unlink()
    try:
        score_pairs(passages, run, key, settings)
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete cohorts must fail rather than change the denominator")
print("ok: short-output threshold, strict equality, target, and missing-output checks")

# Exercise the complete freeze/packet path using unchanged synthetic outputs, never live rewrites.
live = ROOT / "results" / "rewrite" / "large-test"
with TemporaryDirectory() as temp:
    run = Path(temp)
    for name in [
        "manifest.json", "passages.jsonl", "PROCEDURE.md", "settings.toml", "review_key.csv", "review_sheet.csv"
    ]:
        shutil.copyfile(live / name, run / name)
    shutil.copytree(live / "original", run / "original")
    shutil.copytree(live / "original", run / "watermarked")
    passages = read_jsonl(run / "passages.jsonl")
    write_csv(run / "editing_log_batch_test.csv", [
        {"id": p["id"], "editor": "synthetic", "elapsed_seconds": "1", "stop_reason": "unchanged fixture"}
        for p in passages
    ])
    score_large_rewrite.OUT = run
    try:
        original_key_path = score_large_rewrite.KEY_PATH
        bad_key = run / "changed-key.txt"
        bad_key.write_text(bytes(32).hex(), encoding="ascii")
        score_large_rewrite.KEY_PATH = bad_key
        try:
            score_large_rewrite.main()
        except ValueError as error:
            assert "watermark key changed" in str(error)
        else:
            raise AssertionError("Changed key must fail before the first output freeze")
        finally:
            score_large_rewrite.KEY_PATH = original_key_path
        with redirect_stdout(StringIO()):
            score_large_rewrite.main()
            frozen = (run / "output_manifest.json").read_bytes()
            score_large_rewrite.main()
        assert (run / "output_manifest.json").read_bytes() == frozen
        packet = (run / "review_pairs.md").read_text(encoding="utf-8")
        assert packet.count("### Original") == packet.count("### Rewritten") == 100
        assert len(json.loads(frozen)["output_sha256"]) == 100
        assert (run / "review_sheet.csv").read_bytes() == (live / "review_sheet.csv").read_bytes()
        key_file = run / "review_key.csv"
        key_bytes = key_file.read_bytes()
        mapping = read_csv(key_file)
        mapping[0]["id"], mapping[1]["id"] = mapping[1]["id"], mapping[0]["id"]
        write_csv(key_file, mapping)
        try:
            with redirect_stdout(StringIO()):
                score_large_rewrite.main()
        except ValueError:
            pass
        else:
            raise AssertionError("Changed frozen review mappings must be rejected")
        finally:
            key_file.write_bytes(key_bytes)
        changed = run / "watermarked" / f"{passages[0]['id']}.txt"
        changed.write_text(changed.read_text(encoding="utf-8") + " changed", encoding="utf-8")
        try:
            score_large_rewrite.main()
        except ValueError as error:
            assert "Frozen outputs" in str(error)
        else:
            raise AssertionError("Changed frozen outputs must be rejected")
    finally:
        score_large_rewrite.OUT = live
print("ok: 100-output freeze, repeat scoring, blind packet, blank review, and changed key/mapping/output rejection")
