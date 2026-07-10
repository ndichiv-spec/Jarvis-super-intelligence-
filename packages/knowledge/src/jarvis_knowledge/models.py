from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum


class KnowledgeVisibility(StrEnum):
    PRIVATE = "private"
    WORKSPACE = "workspace"
    PROJECT = "project"
    ENTERPRISE = "enterprise"
    PUBLIC = "public"


class KnowledgeSensitivity(StrEnum):
    LOW = "low"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class KnowledgeImportance(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class KnowledgeRelationshipType(StrEnum):
    REFERENCE = "reference"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"
    SUPERSEDES = "supersedes"
    EXPLAINS = "explains"
    RELATED_TO = "related_to"
    VERSION_OF = "version_of"
    PARENT = "parent"
    CHILD = "child"
    CITATION = "citation"


class KnowledgeSourceType(StrEnum):
    DOCUMENTATION = "documentation"
    BOOK = "book"
    RESEARCH_PAPER = "research_paper"
    SPECIFICATION = "specification"
    MANUAL = "manual"
    USER_DOCUMENT = "user_document"
    POLICY = "policy"
    WEB_RESOURCE = "web_resource"
    ENTERPRISE_REPOSITORY = "enterprise_repository"
    OTHER = "other"


class KnowledgeCitationType(StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    VERSION = "version"
    CROSS_PROJECT = "cross_project"


class ValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class KnowledgeClassification:
    domain: str
    topic: str
    category: str
    importance: KnowledgeImportance
    sensitivity: KnowledgeSensitivity
    visibility: KnowledgeVisibility
    language: str
    workspace: str
    project: str
    tags: frozenset[str] = field(default_factory=frozenset)

    def with_overrides(
        self,
        *,
        domain: str | None = None,
        topic: str | None = None,
        category: str | None = None,
        workspace: str | None = None,
        project: str | None = None,
        tags: frozenset[str] | None = None,
    ) -> KnowledgeClassification:
        return replace(
            self,
            domain=domain if domain is not None else self.domain,
            topic=topic if topic is not None else self.topic,
            category=category if category is not None else self.category,
            workspace=workspace if workspace is not None else self.workspace,
            project=project if project is not None else self.project,
            tags=tags if tags is not None else self.tags,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeRelationship:
    target_id: str
    relationship_type: KnowledgeRelationshipType
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class KnowledgeMetadata:
    identifier: str
    title: str
    description: str
    owner: str
    workspace: str
    project: str
    classification: KnowledgeClassification
    tags: frozenset[str]
    language: str
    version: int
    visibility: KnowledgeVisibility
    confidence: float
    relationships: tuple[KnowledgeRelationship, ...]
    created_at: datetime
    updated_at: datetime

    def touch(
        self,
        *,
        updated_at: datetime | None = None,
        version: int | None = None,
    ) -> KnowledgeMetadata:
        return replace(
            self,
            updated_at=updated_at or datetime.now(UTC),
            version=version if version is not None else self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeSource:
    source_id: str
    name: str
    source_type: KnowledgeSourceType
    owner: str
    workspace: str
    project: str
    description: str
    quality_score: float
    metadata: Mapping[str, str] = field(default_factory=dict)
    uri: str | None = None


@dataclass(frozen=True, slots=True)
class KnowledgeCollection:
    collection_id: str
    name: str
    domain: str
    owner: str
    workspace: str
    project: str
    visibility: KnowledgeVisibility
    description: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class KnowledgeVersion:
    version_id: str
    document_id: str
    number: int
    changed_by: str
    change_summary: str
    changed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    compatible_with: tuple[int, ...] = field(default_factory=tuple)
    deprecated: bool = False
    supersedes_version: int | None = None


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    metadata: KnowledgeMetadata
    summary: str
    content_reference: str
    source_id: str
    collection_ids: tuple[str, ...] = field(default_factory=tuple)
    attributes: Mapping[str, str] = field(default_factory=dict)

    def with_update(
        self,
        *,
        summary: str | None = None,
        content_reference: str | None = None,
        tags: frozenset[str] | None = None,
        relationships: tuple[KnowledgeRelationship, ...] | None = None,
        confidence: float | None = None,
        updated_at: datetime | None = None,
    ) -> KnowledgeDocument:
        metadata = replace(
            self.metadata,
            tags=tags if tags is not None else self.metadata.tags,
            confidence=confidence if confidence is not None else self.metadata.confidence,
            relationships=(
                relationships if relationships is not None else self.metadata.relationships
            ),
            classification=self.metadata.classification.with_overrides(
                tags=tags if tags is not None else self.metadata.classification.tags
            ),
        ).touch(updated_at=updated_at)
        return replace(
            self,
            metadata=metadata,
            summary=summary if summary is not None else self.summary,
            content_reference=(
                content_reference if content_reference is not None else self.content_reference
            ),
        )

    def with_relationship(self, relationship: KnowledgeRelationship) -> KnowledgeDocument:
        return self.with_update(
            relationships=(*self.metadata.relationships, relationship),
        )


@dataclass(frozen=True, slots=True)
class KnowledgeCitation:
    citation_id: str
    from_document_id: str
    to_reference: str
    citation_type: KnowledgeCitationType
    metadata: Mapping[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class KnowledgeValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity


@dataclass(frozen=True, slots=True)
class KnowledgeValidationReport:
    document_id: str
    is_valid: bool
    completeness: float
    consistency: float
    integrity: float
    source_quality: float
    version_validity: float
    relationship_integrity: float
    issues: tuple[KnowledgeValidationIssue, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class KnowledgeSearchQuery:
    identifier: str | None = None
    title: str | None = None
    category: str | None = None
    topic: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    workspace: str | None = None
    project: str | None = None
    owner: str | None = None
    language: str | None = None
    relationship_type: KnowledgeRelationshipType | None = None
    metadata_filters: Mapping[str, str] = field(default_factory=dict)
    terms: tuple[str, ...] = field(default_factory=tuple)
    limit: int = 20


@dataclass(frozen=True, slots=True)
class KnowledgeRankingContext:
    requester_id: str
    workspace: str
    project: str
    query_terms: tuple[str, ...] = field(default_factory=tuple)
    now: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ScoredKnowledge:
    document: KnowledgeDocument
    score: float
    confidence: float
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class KnowledgePolicy:
    policy_id: str
    name: str
    retention_days: int | None = None
    allowed_visibility: tuple[KnowledgeVisibility, ...] = (
        KnowledgeVisibility.PRIVATE,
        KnowledgeVisibility.WORKSPACE,
        KnowledgeVisibility.PROJECT,
    )
    workspace_isolation: bool = True
    enterprise_governance: bool = False
    enforce_project_ownership: bool = True
    compliance_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class KnowledgePolicyScope:
    owner: str
    workspace: str
    project: str
    is_enterprise: bool = False


@dataclass(frozen=True, slots=True)
class KnowledgeAccessContext:
    requester_id: str
    workspace: str
    project: str
