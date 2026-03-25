from __future__ import annotations

from typing import Any

import chromadb

from .config import Settings


class VectorDB:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.settings.validate()
        self.settings.ensure_directories()
        self.client = chromadb.PersistentClient(path=str(self.settings.chroma_path))
        self.collection = self.client.get_or_create_collection(
            name=self.settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        doc_id: str,
        embedding: list[float],
        metadata: dict[str, Any],
        document: str = "",
    ) -> None:
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[document],
        )

    def upsert(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        total = self.collection.count()
        if total == 0:
            return {
                "ids": [[]],
                "metadatas": [[]],
                "documents": [[]],
                "distances": [[]],
            }

        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, total),
            "include": ["metadatas", "documents", "distances"],
        }
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def exists(self, doc_id: str) -> bool:
        result = self.collection.get(ids=[doc_id])
        return len(result.get("ids", [])) > 0

    def delete(self, doc_id: str) -> None:
        self.collection.delete(ids=[doc_id])

    def delete_many(self, ids: list[str]) -> None:
        self.collection.delete(ids=ids)

    def count(self) -> int:
        return self.collection.count()

    def list_all(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self.collection.get(
            limit=limit,
            offset=offset,
            include=["metadatas", "documents"],
        )

    def get(self, ids: list[str]) -> dict[str, Any]:
        return self.collection.get(
            ids=ids,
            include=["metadatas", "documents"],
        )

    def update_metadata(self, doc_id: str, metadata: dict[str, Any]) -> None:
        self.collection.update(ids=[doc_id], metadatas=[metadata])


_db: VectorDB | None = None


def _get_db() -> VectorDB:
    global _db
    if _db is None:
        _db = VectorDB(Settings.from_env())
    return _db


def add(
    doc_id: str,
    embedding: list[float],
    metadata: dict[str, Any],
    document: str = "",
) -> None:
    _get_db().add(doc_id, embedding, metadata, document)


def upsert(
    *,
    ids: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
    documents: list[str],
) -> None:
    _get_db().upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
    )


def search(
    query_embedding: list[float],
    n_results: int = 5,
    where: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _get_db().search(query_embedding, n_results=n_results, where=where)


def exists(doc_id: str) -> bool:
    return _get_db().exists(doc_id)


def delete(doc_id: str) -> None:
    _get_db().delete(doc_id)


def delete_many(ids: list[str]) -> None:
    _get_db().delete_many(ids)


def count() -> int:
    return _get_db().count()


def list_all(limit: int = 100, offset: int = 0) -> dict[str, Any]:
    return _get_db().list_all(limit=limit, offset=offset)


def get(ids: list[str]) -> dict[str, Any]:
    return _get_db().get(ids)


def update_metadata(doc_id: str, metadata: dict[str, Any]) -> None:
    _get_db().update_metadata(doc_id, metadata)


__all__ = [
    "VectorDB",
    "add",
    "count",
    "delete",
    "delete_many",
    "exists",
    "get",
    "list_all",
    "search",
    "update_metadata",
    "upsert",
]
