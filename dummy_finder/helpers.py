from __future__ import annotations

import hashlib
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

from . import config


def file_hash(path: str | Path) -> str:
    file_path = Path(path)
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def mime_type(path: str | Path) -> str:
    detected, _ = mimetypes.guess_type(str(path))
    return detected or "application/octet-stream"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_extension(path: str | Path) -> str:
    return Path(path).suffix.lower()


def media_category(path: str | Path) -> str | None:
    return config.get_media_category(normalize_extension(path))


def is_supported(path: str | Path) -> bool:
    file_path = Path(path)
    if file_path.name.startswith("._"):
        return False
    return normalize_extension(file_path) in config.ALL_EXTENSIONS


def ensure_supported(path: str | Path) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Expected a file path, got: {file_path}")
    if not is_supported(file_path):
        raise ValueError(
            f"Unsupported file type: {file_path.suffix.lower() or '<none>'}"
        )
    return file_path


def file_size_bytes(path: str | Path) -> int:
    return Path(path).stat().st_size


def file_size_mb(path: str | Path) -> float:
    return file_size_bytes(path) / (1024 * 1024)


def file_metadata(path: str | Path) -> dict[str, str | int | float | None]:
    file_path = ensure_supported(path)
    return {
        "path": str(file_path),
        "name": file_path.name,
        "suffix": normalize_extension(file_path),
        "mime_type": mime_type(file_path),
        "category": media_category(file_path),
        "sha256": file_hash(file_path),
        "size_bytes": file_size_bytes(file_path),
        "size_mb": round(file_size_mb(file_path), 4),
        "indexed_at": now_iso(),
    }


__all__ = [
    "ensure_supported",
    "file_hash",
    "file_metadata",
    "file_size_bytes",
    "file_size_mb",
    "is_supported",
    "media_category",
    "mime_type",
    "normalize_extension",
    "now_iso",
    "text_hash",
]
