from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DUMMY_FINDER_DATA_DIR", str(PROJECT_DIR / "data")))
CHROMA_DIR = DATA_DIR / "chromadb"
COLLECTION_NAME = "dummy_finder"

SUPPORTED_EXTENSIONS = {
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "document": {".pdf"},
    "text": {
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".html",
        ".py",
        ".js",
        ".ts",
        ".go",
        ".rs",
        ".sh",
    },
}

ALL_EXTENSIONS = {
    ext for extensions in SUPPORTED_EXTENSIONS.values() for ext in extensions
}

EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIMENSIONS = 768
MAX_TEXT_TOKENS = 8192


def _env_value(*names: str, default: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ""):
            return value
    return default


def get_api_key() -> str:
    load_dotenv(PROJECT_DIR / ".env")
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY not set. Add it to .env or set as environment variable."
        )
    return key


def get_media_category(ext: str) -> str | None:
    ext = ext.lower()
    for category, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return None


@dataclass(slots=True)
class Settings:
    project_dir: Path = PROJECT_DIR
    data_dir: Path = DATA_DIR
    chroma_path: Path = CHROMA_DIR
    collection_name: str = COLLECTION_NAME
    embedding_model: str = EMBEDDING_MODEL
    embedding_dimensions: int = EMBEDDING_DIMENSIONS
    max_text_tokens: int = MAX_TEXT_TOKENS
    gemini_api_key: str = field(default_factory=get_api_key)

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        if not self.gemini_api_key:
            raise ValueError("Set GEMINI_API_KEY before using Gemini embeddings.")
        if self.embedding_dimensions <= 0:
            raise ValueError("embedding_dimensions must be greater than zero.")
        if self.max_text_tokens <= 0:
            raise ValueError("max_text_tokens must be greater than zero.")

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(PROJECT_DIR / ".env")
        data_dir = Path(
            _env_value("DUMMY_FINDER_DATA_DIR", "DATA_DIR", default=str(DATA_DIR))
        )
        chroma_path = Path(
            _env_value(
                "DUMMY_FINDER_CHROMA_DIR",
                "CHROMA_DIR",
                default=str(data_dir / "chromadb"),
            )
        )
        return cls(
            data_dir=data_dir,
            chroma_path=chroma_path,
            collection_name=_env_value(
                "DUMMY_FINDER_COLLECTION_NAME",
                "COLLECTION_NAME",
                default=COLLECTION_NAME,
            ),
            embedding_model=_env_value(
                "DUMMY_FINDER_EMBEDDING_MODEL",
                "EMBEDDING_MODEL",
                default=EMBEDDING_MODEL,
            ),
            embedding_dimensions=int(
                _env_value(
                    "DUMMY_FINDER_EMBEDDING_DIMENSIONS",
                    "EMBEDDING_DIMENSIONS",
                    default=str(EMBEDDING_DIMENSIONS),
                )
            ),
            max_text_tokens=int(
                _env_value(
                    "DUMMY_FINDER_MAX_TEXT_TOKENS",
                    "MAX_TEXT_TOKENS",
                    default=str(MAX_TEXT_TOKENS),
                )
            ),
            gemini_api_key=get_api_key(),
        )
