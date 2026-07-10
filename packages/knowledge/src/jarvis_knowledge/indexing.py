from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jarvis_knowledge.chunking import KnowledgeChunk
from jarvis_knowledge.embeddings import DocumentEmbedding, EmbeddingVector


@dataclass(frozen=True, slots=True)
class IndexEntry:
    document_id: str
    chunk_id: str
    text: str
    embedding: EmbeddingVector
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class SearchIndex:
    _entries: dict[str, IndexEntry] = field(default_factory=dict)

    def add(self, entry: IndexEntry) -> None:
        self._entries[entry.chunk_id] = entry

    def add_batch(self, entries: tuple[IndexEntry, ...]) -> None:
        for entry in entries:
            self._entries[entry.chunk_id] = entry

    def get(self, chunk_id: str) -> IndexEntry | None:
        return self._entries.get(chunk_id)

    def remove(self, chunk_id: str) -> None:
        self._entries.pop(chunk_id, None)

    def list_entries(self) -> tuple[IndexEntry, ...]:
        return tuple(self._entries.values())

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


class IndexingEngine(Protocol):
    def index(self, chunk: KnowledgeChunk, embedding: EmbeddingVector) -> IndexEntry: ...
    def index_batch(
        self, chunks: tuple[KnowledgeChunk, ...], embeddings: tuple[EmbeddingVector, ...]
    ) -> tuple[IndexEntry, ...]: ...


class DefaultIndexingEngine:
    def __init__(self, index: SearchIndex | None = None) -> None:
        self._index = index or SearchIndex()

    @property
    def search_index(self) -> SearchIndex:
        return self._index

    def index(self, chunk: KnowledgeChunk, embedding: EmbeddingVector) -> IndexEntry:
        entry = IndexEntry(
            document_id=chunk.document_id,
            chunk_id=chunk.chunk_id,
            text=chunk.text,
            embedding=embedding,
        )
        self._index.add(entry)
        return entry

    def index_batch(
        self, chunks: tuple[KnowledgeChunk, ...], embeddings: tuple[EmbeddingVector, ...]
    ) -> tuple[IndexEntry, ...]:
        if len(chunks) != len(embeddings):
            msg = f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch"
            raise ValueError(msg)
        entries = tuple(
            self.index(chunk, embedding) for chunk, embedding in zip(chunks, embeddings, strict=True)
        )
        return entries
