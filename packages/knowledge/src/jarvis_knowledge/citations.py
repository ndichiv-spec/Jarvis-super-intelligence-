from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from jarvis_knowledge.models import KnowledgeCitation, KnowledgeCitationType
from jarvis_knowledge.engines import InMemoryCitationEngine


class EnhancedCitationEngine(Protocol):
    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation: ...
    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]: ...
    def count_citations(self, document_id: str) -> int: ...
    def citations_by_type(self, citation_type: KnowledgeCitationType) -> tuple[KnowledgeCitation, ...]: ...


class TrackedCitationEngine:
    def __init__(self) -> None:
        self._base = InMemoryCitationEngine()
        self._by_type: dict[KnowledgeCitationType, tuple[KnowledgeCitation, ...]] = {}

    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation:
        citation = self._base.create_citation(
            from_document_id=from_document_id,
            to_reference=to_reference,
            citation_type=citation_type,
            metadata=metadata,
        )
        existing = self._by_type.get(citation_type, ())
        self._by_type[citation_type] = (*existing, citation)
        return citation

    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]:
        return self._base.list_citations(document_id)

    def count_citations(self, document_id: str) -> int:
        return len(self._base.list_citations(document_id))

    def citations_by_type(self, citation_type: KnowledgeCitationType) -> tuple[KnowledgeCitation, ...]:
        return self._by_type.get(citation_type, ())

    def all_citations(self) -> tuple[KnowledgeCitation, ...]:
        result: list[KnowledgeCitation] = []
        for citations in self._by_type.values():
            result.extend(citations)
        return tuple(result)


class CrossReferenceEngine:
    def __init__(self) -> None:
        self._citations: dict[str, list[KnowledgeCitation]] = {}
        self._backlinks: dict[str, list[KnowledgeCitation]] = {}

    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation:
        from uuid import uuid4
        citation = KnowledgeCitation(
            citation_id=f"xref-{uuid4().hex[:12]}",
            from_document_id=from_document_id,
            to_reference=to_reference,
            citation_type=citation_type,
            metadata=metadata or {},
        )
        self._citations.setdefault(from_document_id, []).append(citation)
        self._backlinks.setdefault(to_reference, []).append(citation)
        return citation

    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]:
        return tuple(self._citations.get(document_id, []))

    def count_citations(self, document_id: str) -> int:
        return len(self._citations.get(document_id, []))

    def citations_by_type(self, citation_type: KnowledgeCitationType) -> tuple[KnowledgeCitation, ...]:
        result: list[KnowledgeCitation] = []
        for citations in self._citations.values():
            result.extend(c for c in citations if c.citation_type == citation_type)
        return tuple(result)

    def backlinks(self, document_id: str) -> tuple[KnowledgeCitation, ...]:
        return tuple(self._backlinks.get(document_id, []))

    def backlink_count(self, document_id: str) -> int:
        return len(self._backlinks.get(document_id, []))
