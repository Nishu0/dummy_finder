from __future__ import annotations

from pathlib import Path

from . import config
from . import db
from .embedder import GeminiEmbedder
from .helpers import ensure_supported, file_metadata, media_category, text_hash
from .config import Settings


class LocalSearch:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.settings.validate()
        self.settings.ensure_directories()
        self.embedder = GeminiEmbedder(self.settings)
        self.db = db.VectorDB(self.settings)

    def _preview_for_path(self, path: Path, category: str | None) -> str:
        if category == "text":
            return path.read_text(encoding="utf-8")
        return str(path)

    def _build_metadata(
        self,
        path: Path,
        *,
        description: str = "",
        source: str = "local",
    ) -> dict[str, str | int | float | None]:
        metadata = file_metadata(path)
        metadata.update(
            {
                "file_path": str(path),
                "file_name": path.name,
                "media_category": media_category(path),
                "timestamp": str(metadata.get("indexed_at", "")),
                "description": description,
                "source": source,
            }
        )
        return metadata

    def add_path(
        self,
        path: str | Path,
        *,
        doc_id: str | None = None,
        description: str = "",
        source: str = "local",
    ) -> str:
        file_path = ensure_supported(path)
        category = media_category(file_path)
        vector = self.embedder.embed_path(file_path)
        metadata = self._build_metadata(
            file_path,
            description=description,
            source=source,
        )
        document = self._preview_for_path(file_path, category)
        entry_id = doc_id or str(metadata["sha256"])

        self.db.upsert(
            ids=[entry_id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[document],
        )
        return entry_id

    def add_pdf(
        self,
        pdf_path: str | Path,
        doc_id: str | None = None,
        description: str = "",
        source: str = "local",
    ) -> str:
        return self.add_path(
            pdf_path, doc_id=doc_id, description=description, source=source
        )

    def add_image(
        self,
        image_path: str | Path,
        doc_id: str | None = None,
        description: str = "",
        source: str = "local",
    ) -> str:
        return self.add_path(
            image_path, doc_id=doc_id, description=description, source=source
        )

    def add_text(
        self,
        text: str,
        *,
        doc_id: str | None = None,
        title: str = "text",
        description: str = "",
        source: str = "inline",
    ) -> str:
        vector = self.embedder.embed_text(text)
        entry_id = doc_id or text_hash(text)
        metadata = {
            "file_path": "",
            "file_name": title,
            "media_category": "text",
            "timestamp": "",
            "description": description,
            "source": source,
            "mime_type": "text/plain",
            "sha256": entry_id,
        }
        self.db.upsert(
            ids=[entry_id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[text],
        )
        return entry_id

    def raw_search(
        self,
        query: str,
        n_results: int = 5,
        media_type: str | None = None,
    ) -> dict:
        query_embedding = self.embedder.embed_query(query)
        where = None
        if media_type:
            where = {"media_category": media_type}
        return self.db.search(
            query_embedding,
            n_results=n_results,
            where=where,
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        media_type: str | None = None,
    ) -> list[dict]:
        raw = self.raw_search(query, n_results=n_results, media_type=media_type)
        results: list[dict] = []

        ids = raw.get("ids", [[]])
        metadatas = raw.get("metadatas", [[]])
        distances = raw.get("distances", [[]])
        documents = raw.get("documents", [[]])

        if not ids or not ids[0]:
            return results

        for index, entry_id in enumerate(ids[0]):
            meta = metadatas[0][index] if metadatas and metadatas[0] else {}
            distance = distances[0][index] if distances and distances[0] else 1.0
            document = documents[0][index] if documents and documents[0] else ""
            similarity = max(0.0, 1 - float(distance))
            preview = (document or "")[:200].replace("\n", " ")

            results.append(
                {
                    "id": entry_id,
                    "similarity": round(similarity, 4),
                    "distance": round(float(distance), 4),
                    "file_path": meta.get("file_path", meta.get("path", "")),
                    "file_name": meta.get("file_name", meta.get("name", "")),
                    "media_category": meta.get(
                        "media_category", meta.get("category", "")
                    ),
                    "timestamp": meta.get("timestamp", meta.get("indexed_at", "")),
                    "description": meta.get("description", ""),
                    "source": meta.get("source", "local"),
                    "mime_type": meta.get("mime_type", ""),
                    "preview": preview,
                }
            )

        return results

    def format_results(self, results: list[dict]) -> str:
        if not results:
            return "No results found."

        lines: list[str] = []
        for index, result in enumerate(results, 1):
            score_pct = f"{result['similarity'] * 100:.1f}%"
            path = result["file_path"] or "(text snippet)"
            category = result["media_category"] or "unknown"
            timestamp = result["timestamp"][:10] if result["timestamp"] else "unknown"

            lines.append(
                f"**{index}. [{category}] {result['file_name'] or 'text'}** -- {score_pct} match"
            )
            lines.append(f"   Path: `{path}`")
            lines.append(f"   Date: {timestamp} | Source: {result['source']}")
            if result["mime_type"]:
                lines.append(f"   MIME: {result['mime_type']}")
            if result["preview"]:
                lines.append(f"   Preview: {result['preview'][:150]}")
            if result["description"]:
                lines.append(f"   Description: {result['description']}")
            lines.append("")

        return "\n".join(lines)


_default_search: LocalSearch | None = None


def _get_default_search() -> LocalSearch:
    global _default_search
    if _default_search is None:
        _default_search = LocalSearch(Settings.from_env())
    return _default_search


def search(
    query: str,
    n_results: int = 5,
    media_type: str | None = None,
) -> list[dict]:
    return _get_default_search().search(
        query=query,
        n_results=n_results,
        media_type=media_type,
    )


def format_results(results: list[dict]) -> str:
    return _get_default_search().format_results(results)


def add_path(
    path: str | Path,
    *,
    doc_id: str | None = None,
    description: str = "",
    source: str = "local",
) -> str:
    return _get_default_search().add_path(
        path,
        doc_id=doc_id,
        description=description,
        source=source,
    )


def add_text(
    text: str,
    *,
    doc_id: str | None = None,
    title: str = "text",
    description: str = "",
    source: str = "inline",
) -> str:
    return _get_default_search().add_text(
        text,
        doc_id=doc_id,
        title=title,
        description=description,
        source=source,
    )


SUPPORTED_MEDIA_TYPES = tuple(config.SUPPORTED_EXTENSIONS.keys())


__all__ = [
    "LocalSearch",
    "SUPPORTED_MEDIA_TYPES",
    "add_path",
    "add_text",
    "format_results",
    "search",
]
