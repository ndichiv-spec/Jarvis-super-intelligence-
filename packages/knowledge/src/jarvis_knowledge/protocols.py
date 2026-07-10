from __future__ import annotations

from typing import Protocol

from jarvis_knowledge.models import (
    KnowledgeAccessContext,
    KnowledgeCitation,
    KnowledgeCitationType,
    KnowledgeClassification,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgePolicy,
    KnowledgePolicyScope,
    KnowledgeRankingContext,
    KnowledgeRelationship,
    KnowledgeRelationshipType,
    KnowledgeSearchQuery,
    KnowledgeSource,
    KnowledgeValidationReport,
    KnowledgeVersion,
    ScoredKnowledge,
)


class KnowledgeCatalog(Protocol):
    def register_source(self, source: KnowledgeSource) -> None: ...

    def get_source(self, source_id: str) -> KnowledgeSource | None: ...

    def register_collection(self, collection: KnowledgeCollection) -> None: ...

    def get_collection(self, collection_id: str) -> KnowledgeCollection | None: ...

    def register_document(self, document: KnowledgeDocument) -> None: ...

    def update_document(self, document: KnowledgeDocument) -> None: ...

    def get_document(self, identifier: str) -> KnowledgeDocument | None: ...

    def list_documents(self) -> tuple[KnowledgeDocument, ...]: ...


class KnowledgeClassificationEngine(Protocol):
    def classify(
        self,
        *,
        document: KnowledgeDocument,
        source: KnowledgeSource,
        collections: tuple[KnowledgeCollection, ...],
    ) -> KnowledgeClassification: ...


class KnowledgeValidationEngine(Protocol):
    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport: ...


class KnowledgeSearchEngine(Protocol):
    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]: ...


class KnowledgeRankingEngine(Protocol):
    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]: ...


class KnowledgeGraph(Protocol):
    def link(
        self,
        *,
        source_id: str,
        target_id: str,
        relationship_type: KnowledgeRelationshipType,
    ) -> None: ...

    def neighbors(
        self,
        *,
        source_id: str,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> tuple[KnowledgeRelationship, ...]: ...


class CitationEngine(Protocol):
    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation: ...

    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]: ...


class KnowledgeVersionManager(Protocol):
    def register_initial(self, document: KnowledgeDocument) -> None: ...

    def record_version(
        self,
        *,
        document: KnowledgeDocument,
        changed_by: str,
        change_summary: str,
        compatible_with: tuple[int, ...] = (),
        deprecated: bool = False,
    ) -> KnowledgeDocument: ...

    def current_version(self, document_id: str) -> KnowledgeVersion | None: ...

    def history(self, document_id: str) -> tuple[KnowledgeVersion, ...]: ...

    def is_compatible(self, document_id: str, required_version: int) -> bool: ...


class KnowledgePolicyEngine(Protocol):
    def register_policy(self, scope: KnowledgePolicyScope, policy: KnowledgePolicy) -> None: ...

    def resolve(self, scope: KnowledgePolicyScope) -> KnowledgePolicy: ...

    def can_access(
        self,
        *,
        document: KnowledgeDocument,
        access: KnowledgeAccessContext,
        policy: KnowledgePolicy,
    ) -> bool: ...
