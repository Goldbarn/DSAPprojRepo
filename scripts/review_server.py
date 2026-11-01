"""Serve only the blind review page, and append each autosave to results/human-review/review_log.jsonl.

Nothing else in the repo is reachable, so the answer key and scores stay private. Run with --self-check to test it.
"""

import argparse
import json
import secrets
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from wmark.settings import RESULTS_DIR

DIR = RESULTS_DIR / "human-review"
MAX_BODY = 256_000
MAX_NOTES = 2_000


def is_valid(state: object, labels: set[str]) -> bool:
    if not isinstance(state, dict) or set(state) != {"reviewer", "answers"}:
        return False
    if not isinstance(state["reviewer"], str) or len(state["reviewer"]) > 100:
        return False
    if not isinstance(state["answers"], dict) or not set(state["answers"]) <= labels:
        return False
    for answer in state["answers"].values():
        if not isinstance(answer, dict) or not set(answer) <= {"meaning", "readable", "notes"}:
            return False
        if answer.get("meaning", "yes") not in ("yes", "no") or answer.get("readable", "yes") not in ("yes", "no"):
            return False
        notes = answer.get("notes", "")
        if not isinstance(notes, str) or len(notes) > MAX_NOTES:
            return False
    return True


def make_handler(token: str, page: bytes, labels: set[str], log: Path) -> type[BaseHTTPRequestHandler]:
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status: int, body: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path.rstrip("/") == f"/{token}":
                self.reply(200, page, "text/html; charset=utf-8")
            else:
                self.reply(404)

        def do_POST(self) -> None:
            if self.path != f"/{token}/answers":
                return self.reply(404)
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self.reply(400)
            if not 0 < length <= MAX_BODY:
                return self.reply(413)
            try:
                state = json.loads(self.rfile.read(length))
            except ValueError:
                return self.reply(400)
            if not is_valid(state, labels):
                return self.reply(400)
            entry = {"saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **state}
            with lock, log.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.reply(204)

        def log_message(self, *args: object) -> None:
            pass

    return Handler


def self_check() -> None:
    import tempfile
    import urllib.error
    import urllib.request

    log = Path(tempfile.mkdtemp()) / "log.jsonl"
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("tok", b"<p>page</p>", {"R01"}, log))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"

    def status(path: str, body: bytes | None = None) -> int:
        try:
            return urllib.request.urlopen(urllib.request.Request(base + path, data=body)).status
        except urllib.error.HTTPError as e:
            return e.code

    good = json.dumps({"reviewer": "A", "answers": {"R01": {"meaning": "yes", "notes": "ok"}}}).encode()
    assert status("/tok") == 200
    assert status("/") == status("/key.json") == status("/tok/key.json") == status("/tok/../key.json") == 404
    assert status("/wrong/answers", good) == 404
    assert status("/tok/answers", b"not json") == 400
    assert status("/tok/answers", b'{"reviewer":"A","answers":{"R99":{}}}') == 400
    assert status("/tok/answers", b'{"reviewer":"A","answers":{"R01":{"meaning":"maybe"}}}') == 400
    assert status("/tok/answers", good) == 204
    entries = log.read_text(encoding="utf-8").splitlines()
    assert len(entries) == 1 and json.loads(entries[0])["answers"]["R01"]["meaning"] == "yes"
    server.shutdown()
    print("ok")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        return self_check()

    token = secrets.token_urlsafe(9)
    page = (DIR / "review.html").read_bytes()
    labels = set(json.loads((DIR / "key.json").read_text(encoding="utf-8")))
    handler = make_handler(token, page, labels, DIR / "review_log.jsonl")
    print(f"http://localhost:{args.port}/{token}", flush=True)
    ThreadingHTTPServer((args.host, args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
