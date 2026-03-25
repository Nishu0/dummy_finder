from __future__ import annotations

from pathlib import Path

from google import genai
from google.genai import types

from . import config
from .config import Settings
from .helpers import ensure_supported, file_metadata, mime_type


class GeminiEmbedder:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.settings.validate()
        self.settings.ensure_directories()
        self.client = genai.Client(api_key=self.settings.gemini_api_key)

    def _embed_content(self, contents: str | types.Content, task: str) -> list[float]:
        result = self.client.models.embed_content(
            model=self.settings.embedding_model,
            contents=contents,
            config=types.EmbedContentConfig(
                task_type=task,
                output_dimensionality=self.settings.embedding_dimensions,
            ),
        )
        return list(result.embeddings[0].values)

    def _embed_binary_file(
        self,
        path: str | Path,
        *,
        task: str = "RETRIEVAL_DOCUMENT",
        forced_mime_type: str | None = None,
    ) -> list[float]:
        file_path = ensure_supported(path)
        payload = types.Content(
            parts=[
                types.Part(
                    inline_data=types.Blob(
                        mime_type=forced_mime_type or mime_type(file_path),
                        data=file_path.read_bytes(),
                    )
                )
            ]
        )
        return self._embed_content(payload, task=task)

    def embed_path(
        self, path: str | Path, task: str = "RETRIEVAL_DOCUMENT"
    ) -> list[float]:
        file_path = ensure_supported(path)
        category = config.get_media_category(file_path.suffix)
        if category in {"image", "audio", "video"}:
            return self._embed_binary_file(file_path, task=task)
        if category == "document":
            return self._embed_binary_file(
                file_path,
                task=task,
                forced_mime_type="application/pdf",
            )
        if category == "text":
            return self.embed_text(file_path.read_text(encoding="utf-8"), task=task)
        raise ValueError(f"Unsupported file category for embedding: {file_path}")

    def describe_path(self, path: str | Path) -> dict[str, str | int | float | None]:
        return file_metadata(path)

    def embed_text(self, text: str, task: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        return self._embed_content(text, task=task)

    def embed_query(self, query: str) -> list[float]:
        return self.embed_text(query, task="RETRIEVAL_QUERY")

    def embed_image(self, image_path: str | Path) -> list[float]:
        return self._embed_binary_file(image_path)

    def embed_audio(self, audio_path: str | Path) -> list[float]:
        return self._embed_binary_file(audio_path)

    def embed_video(self, video_path: str | Path) -> list[float]:
        return self._embed_binary_file(video_path)

    def embed_pdf(self, pdf_path: str | Path) -> list[float]:
        return self._embed_binary_file(
            pdf_path,
            forced_mime_type="application/pdf",
        )


_default_embedder: GeminiEmbedder | None = None


def _get_default_embedder() -> GeminiEmbedder:
    global _default_embedder
    if _default_embedder is None:
        _default_embedder = GeminiEmbedder(Settings.from_env())
    return _default_embedder


def embed_text(text: str, task: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    return _get_default_embedder().embed_text(text, task=task)


def embed_query(query: str) -> list[float]:
    return _get_default_embedder().embed_query(query)


def embed_image(path: str | Path) -> list[float]:
    return _get_default_embedder().embed_image(path)


def embed_audio(path: str | Path) -> list[float]:
    return _get_default_embedder().embed_audio(path)


def embed_video(path: str | Path) -> list[float]:
    return _get_default_embedder().embed_video(path)


def embed_pdf(path: str | Path) -> list[float]:
    return _get_default_embedder().embed_pdf(path)


def embed_path(path: str | Path, task: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    return _get_default_embedder().embed_path(path, task=task)


def describe_path(path: str | Path) -> dict[str, str | int | float | None]:
    return _get_default_embedder().describe_path(path)


__all__ = [
    "GeminiEmbedder",
    "embed_text",
    "embed_query",
    "embed_image",
    "embed_audio",
    "embed_video",
    "embed_pdf",
    "embed_path",
    "describe_path",
    "mime_type",
    "config",
]
