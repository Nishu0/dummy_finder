from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from . import config, db, embedder
from .config import Settings
from .helpers import (
    ensure_supported,
    file_hash,
    file_metadata,
    is_supported,
    now_iso,
    text_hash,
)


class Ingestor:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.settings.validate()
        self.settings.ensure_directories()
        self.db = db.VectorDB(self.settings)
        self.embedder = embedder.GeminiEmbedder(self.settings)

    def _truncate_text(self, text: str, limit: int = 32000) -> str:
        if len(text) <= limit:
            return text
        return text[:limit]

    def _preview_text(self, text: str, limit: int = 500) -> str:
        return text[:limit]

    def _file_document_text(
        self, path: Path, category: str | None, description: str
    ) -> str:
        if category == "text":
            text = path.read_text(encoding="utf-8", errors="replace")
            return self._preview_text(self._truncate_text(text))
        if description:
            return description
        label = category or "file"
        return f"{label.title()}: {path.name}"

    def _build_file_metadata(
        self,
        path: Path,
        *,
        category: str | None,
        source: str,
        description: str,
    ) -> dict[str, str | int | float | None]:
        metadata = file_metadata(path)
        metadata.update(
            {
                "file_path": str(path),
                "file_name": path.name,
                "file_type": metadata.get("mime_type", "application/octet-stream"),
                "media_category": category,
                "timestamp": now_iso(),
                "source": source,
                "description": description,
                "file_size": path.stat().st_size,
            }
        )
        return metadata

    def ingest_file(
        self,
        path: str | Path,
        source: str = "manual",
        description: str = "",
        force: bool = False,
    ) -> dict[str, str]:
        file_path = ensure_supported(path).resolve()
        category = config.get_media_category(file_path.suffix.lower())
        doc_id = file_hash(file_path)

        if not force and self.db.exists(doc_id):
            return {
                "status": "skipped",
                "reason": "already embedded",
                "id": doc_id,
                "path": str(file_path),
            }

        if category == "text":
            text = file_path.read_text(encoding="utf-8", errors="replace")
            embedding = self.embedder.embed_text(self._truncate_text(text))
        elif category == "image":
            embedding = self.embedder.embed_image(file_path)
        elif category == "audio":
            embedding = self.embedder.embed_audio(file_path)
        elif category == "video":
            embedding = self.embedder.embed_video(file_path)
        elif category == "document":
            embedding = self.embedder.embed_pdf(file_path)
        else:
            raise ValueError(f"Unknown category: {category}")

        metadata = self._build_file_metadata(
            file_path,
            category=category,
            source=source,
            description=description,
        )
        document = self._file_document_text(file_path, category, description)
        self.db.add(doc_id, embedding, metadata, document=document)

        return {
            "status": "embedded",
            "id": doc_id,
            "path": str(file_path),
            "category": str(category),
        }

    def ingest_text(
        self,
        text: str,
        description: str = "",
        source: str = "manual",
        tags: str = "",
        title: str = "text",
        force: bool = False,
    ) -> dict[str, str]:
        doc_id = text_hash(text)
        if not force and self.db.exists(doc_id):
            return {
                "status": "skipped",
                "reason": "already embedded",
                "id": doc_id,
            }

        embedding = self.embedder.embed_text(self._truncate_text(text))
        metadata = {
            "file_path": "",
            "file_name": title,
            "file_type": "text/plain",
            "media_category": "text",
            "timestamp": now_iso(),
            "source": source,
            "description": description,
            "tags": tags,
            "file_size": len(text.encode("utf-8")),
            "sha256": doc_id,
        }
        self.db.add(doc_id, embedding, metadata, document=self._preview_text(text))

        return {"status": "embedded", "id": doc_id, "category": "text"}

    def ingest_directory(
        self,
        path: str | Path,
        source: str = "manual",
        recursive: bool = True,
        progress_callback: Callable[[int, int, dict[str, str]], None] | None = None,
        force: bool = False,
    ) -> list[dict[str, str]]:
        directory = Path(path).resolve()
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Expected a directory path, got: {directory}")

        pattern = "**/*" if recursive else "*"
        files = [
            file_path
            for file_path in sorted(directory.glob(pattern))
            if file_path.is_file() and is_supported(file_path)
        ]

        results: list[dict[str, str]] = []
        total = len(files)

        for index, file_path in enumerate(files, 1):
            try:
                result = self.ingest_file(file_path, source=source, force=force)
            except Exception as exc:
                result = {
                    "status": "error",
                    "path": str(file_path),
                    "error": str(exc),
                }
            results.append(result)
            if progress_callback:
                progress_callback(index, total, result)

        return results


_default_ingestor: Ingestor | None = None


def _get_default_ingestor() -> Ingestor:
    global _default_ingestor
    if _default_ingestor is None:
        _default_ingestor = Ingestor(Settings.from_env())
    return _default_ingestor


def ingest_file(
    path: str | Path,
    source: str = "manual",
    description: str = "",
    force: bool = False,
) -> dict[str, str]:
    return _get_default_ingestor().ingest_file(
        path,
        source=source,
        description=description,
        force=force,
    )


def ingest_text(
    text: str,
    description: str = "",
    source: str = "manual",
    tags: str = "",
    title: str = "text",
    force: bool = False,
) -> dict[str, str]:
    return _get_default_ingestor().ingest_text(
        text,
        description=description,
        source=source,
        tags=tags,
        title=title,
        force=force,
    )


def ingest_directory(
    path: str | Path,
    source: str = "manual",
    recursive: bool = True,
    progress_callback: Callable[[int, int, dict[str, str]], None] | None = None,
    force: bool = False,
) -> list[dict[str, str]]:
    return _get_default_ingestor().ingest_directory(
        path,
        source=source,
        recursive=recursive,
        progress_callback=progress_callback,
        force=force,
    )


__all__ = ["Ingestor", "ingest_directory", "ingest_file", "ingest_text"]
