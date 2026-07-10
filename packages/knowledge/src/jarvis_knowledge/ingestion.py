from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from jarvis_knowledge.models import (
    KnowledgeDocument,
    KnowledgeMetadata,
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeVisibility,
    KnowledgeImportance,
    KnowledgeSensitivity,
    KnowledgeClassification,
)


@dataclass(frozen=True, slots=True)
class IngestionManifest:
    manifest_id: str
    source_name: str
    source_type: KnowledgeSourceType
    raw_content: str
    owner: str
    workspace: str
    project: str
    language: str = "en"
    title: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    ingested_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class IngestionResult:
    manifest_id: str
    document: KnowledgeDocument
    success: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


class IngestionEngine(Protocol):
    def ingest(self, manifest: IngestionManifest) -> IngestionResult: ...
    def ingest_batch(self, manifests: tuple[IngestionManifest, ...]) -> tuple[IngestionResult, ...]: ...


class DefaultIngestionEngine:
    def __init__(self, document_callback=None) -> None:
        self._callback = document_callback

    def ingest(self, manifest: IngestionManifest) -> IngestionResult:
        errors: list[str] = []
        if not manifest.raw_content.strip():
            errors.append("raw_content is empty")

        title = manifest.title or manifest.source_name
        identifier = f"ing-{uuid4().hex[:12]}"

        classification = KnowledgeClassification(
            domain="general",
            topic="general",
            category="general",
            importance=KnowledgeImportance.NORMAL,
            sensitivity=KnowledgeSensitivity.INTERNAL,
            visibility=KnowledgeVisibility.WORKSPACE,
            language=manifest.language,
            workspace=manifest.workspace,
            project=manifest.project,
            tags=manifest.tags,
        )

        metadata = KnowledgeMetadata(
            identifier=identifier,
            title=title,
            description=f"Ingested from: {manifest.source_name}",
            owner=manifest.owner,
            workspace=manifest.workspace,
            project=manifest.project,
            classification=classification,
            tags=manifest.tags,
            language=manifest.language,
            version=1,
            visibility=KnowledgeVisibility.WORKSPACE,
            confidence=0.5,
            relationships=(),
            created_at=manifest.ingested_at,
            updated_at=manifest.ingested_at,
        )

        document = KnowledgeDocument(
            metadata=metadata,
            summary=manifest.raw_content[:200],
            content_reference=f"ingest://{manifest.source_type.value}/{identifier}",
            source_id=manifest.manifest_id,
            collection_ids=(),
            attributes={"raw_length": str(len(manifest.raw_content))},
        )

        if self._callback:
            self._callback(document)

        return IngestionResult(
            manifest_id=manifest.manifest_id,
            document=document,
            success=len(errors) == 0,
            errors=tuple(errors),
        )

    def ingest_batch(self, manifests: tuple[IngestionManifest, ...]) -> tuple[IngestionResult, ...]:
        return tuple(self.ingest(m) for m in manifests)
