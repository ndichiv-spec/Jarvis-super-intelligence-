from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    text: str
    index: int
    heading: str | None = None
    tokens_estimate: int = 0
    metadata: dict[str, str] = field(default_factory=dict)


class ChunkingStrategy(Protocol):
    def chunk(self, text: str, document_id: str) -> tuple[KnowledgeChunk, ...]: ...


class FixedSizeChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, document_id: str) -> tuple[KnowledgeChunk, ...]:
        chunks: list[KnowledgeChunk] = []
        chars = text
        start = 0
        index = 0
        while start < len(chars):
            end = min(start + self._chunk_size, len(chars))
            chunk_text = chars[start:end]
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{document_id}/chunk/{index}",
                    document_id=document_id,
                    text=chunk_text,
                    index=index,
                    tokens_estimate=len(chunk_text) // 4,
                )
            )
            index += 1
            start += self._chunk_size - self._overlap
            if start >= len(chars):
                break
        return tuple(chunks)


class ParagraphChunker:
    def chunk(self, text: str, document_id: str) -> tuple[KnowledgeChunk, ...]:
        chunks: list[KnowledgeChunk] = []
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for i, paragraph in enumerate(paragraphs):
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{document_id}/para/{i}",
                    document_id=document_id,
                    text=paragraph,
                    index=i,
                    tokens_estimate=len(paragraph) // 4,
                )
            )
        return tuple(chunks)


class HeadingAwareChunker:
    def chunk(self, text: str, document_id: str) -> tuple[KnowledgeChunk, ...]:
        chunks: list[KnowledgeChunk] = []
        lines = text.split("\n")
        current_heading: str | None = None
        current_buffer: list[str] = []
        index = 0

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("##") or stripped.startswith("#"):
                if current_buffer:
                    chunk_text = "\n".join(current_buffer).strip()
                    if chunk_text:
                        chunks.append(
                            KnowledgeChunk(
                                chunk_id=f"{document_id}/section/{index}",
                                document_id=document_id,
                                text=chunk_text,
                                index=index,
                                heading=current_heading,
                                tokens_estimate=len(chunk_text) // 4,
                            )
                        )
                        index += 1
                    current_buffer = []
                current_heading = stripped.lstrip("#").strip()
            else:
                current_buffer.append(line)

        if current_buffer:
            chunk_text = "\n".join(current_buffer).strip()
            if chunk_text:
                chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"{document_id}/section/{index}",
                        document_id=document_id,
                        text=chunk_text,
                        index=index,
                        heading=current_heading,
                        tokens_estimate=len(chunk_text) // 4,
                    )
                )

        return tuple(chunks)
