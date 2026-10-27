import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "config" / "settings.toml"
KEY_PATH = ROOT / "secrets" / "watermark.key"
SYNONYMS_PATH = ROOT / "data" / "synonyms.json"
SOURCES_CSV = ROOT / "data" / "sources" / "sources.csv"
RAW_DIR = ROOT / "data" / "sources" / "raw"
CANDIDATES_PATH = ROOT / "data" / "passages" / "candidates.jsonl"
SPLITS_DIR = ROOT / "data" / "splits"
RESULTS_DIR = ROOT / "results"


@dataclass(frozen=True)
class Settings:
    threshold: float
    target: float
    max_seconds: float
    max_substitutions: int
    frozen: bool
    seed: int
    raw: dict


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    s = Settings(
        threshold=raw["detector"]["threshold"],
        target=raw["watermark"]["target"],
        max_seconds=raw["watermark"]["max_seconds"],
        max_substitutions=raw["watermark"]["max_substitutions"],
        frozen=raw["experiment"]["frozen"],
        seed=raw["experiment"]["seed"],
        raw=raw,
    )
    if s.target <= s.threshold:
        raise ValueError("watermark target must be strictly above the detection threshold")
    return s
