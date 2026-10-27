import hmac
import secrets
from pathlib import Path

GREEN = 1
RED = 0
KEY_BYTES = 32


def word_color(word: str, key: bytes) -> int:
    """Color of an already-normalized word: 1 = green, 0 = red."""
    return hmac.digest(key, word.encode("utf-8"), "sha256")[-1] & 1


def generate_key(path: Path) -> bytes:
    if path.exists():
        raise FileExistsError(f"{path} already exists; the experiment uses one key throughout")
    key = secrets.token_bytes(KEY_BYTES)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(key.hex() + "\n", encoding="ascii")
    return key


def load_key(path: Path) -> bytes:
    key = bytes.fromhex(path.read_text(encoding="ascii").strip())
    if len(key) != KEY_BYTES:
        raise ValueError(f"expected a {KEY_BYTES}-byte key in {path}, got {len(key)} bytes")
    return key
