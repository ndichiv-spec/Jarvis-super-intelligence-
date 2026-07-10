from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum


class MemoryType(StrEnum):
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CONVERSATION = "conversation"
    PROJECT = "project"
    WORKSPACE = "workspace"
    AGENT = "agent"


class MemoryRelationshipType(StrEnum):
    PARENT = "parent"
    CHILD = "child"
    REFERENCE = "reference"
    CONVERSATION = "conversation"
    PROJECT = "project"
    WORKFLOW = "workflow"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"
    ASSOCIATION = "association"


class MemoryVisibility(StrEnum):
    PRIVATE = "private"
    SHARED = "shared"
    SYSTEM = "system"


class MemoryPrivacyLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    RESTRICTED = "restricted"


@dataclass(frozen=True, slots=True)
class MemoryRelationship:
    target_id: str
    relationship_type: MemoryRelationshipType
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class MemoryMetadata:
    identifier: str
    created_at: datetime
    updated_at: datetime
    confidence: float
    importance: float
    source: str
    visibility: MemoryVisibility
    privacy_level: MemoryPrivacyLevel
    relationships: tuple[MemoryRelationship, ...]
    classification: MemoryType
    tags: frozenset[str] = field(default_factory=frozenset)
    version: int = 1
    lineage: tuple[str, ...] = field(default_factory=tuple)
    access_count: int = 0
    user_feedback: float = 0.0

    def touch(self, *, updated_at: datetime | None = None) -> MemoryMetadata:
        return replace(
            self,
            updated_at=updated_at or datetime.now(UTC),
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    metadata: MemoryMetadata
    content: str
    memory_type: MemoryType
    context: str | None = None
    intent: str | None = None
    conversation_id: str | None = None
    project_id: str | None = None
    workflow_id: str | None = None
    workspace_id: str | None = None
    agent_id: str | None = None
    participants: tuple[str, ...] = field(default_factory=tuple)
    outcome: str | None = None
    event_time: datetime | None = None
    expires_at: datetime | None = None
    retention_until: datetime | None = None
    archived: bool = False
    attributes: Mapping[str, str] = field(default_factory=dict)

    def is_expired(self, *, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        current = now or datetime.now(UTC)
        return self.expires_at <= current

    def with_update(
        self,
        *,
        content: str | None = None,
        confidence: float | None = None,
        importance: float | None = None,
        tags: frozenset[str] | None = None,
        relationships: tuple[MemoryRelationship, ...] | None = None,
        updated_at: datetime | None = None,
    ) -> MemoryRecord:
        metadata = replace(
            self.metadata,
            confidence=confidence if confidence is not None else self.metadata.confidence,
            importance=importance if importance is not None else self.metadata.importance,
            tags=tags if tags is not None else self.metadata.tags,
            relationships=relationships
            if relationships is not None
            else self.metadata.relationships,
        ).touch(updated_at=updated_at)
        return replace(
            self, metadata=metadata, content=content if content is not None else self.content
        )

    def with_relationship(self, relationship: MemoryRelationship) -> MemoryRecord:
        return self.with_update(relationships=(*self.metadata.relationships, relationship))


@dataclass(frozen=True, slots=True)
class MemoryPolicy:
    policy_id: str
    name: str
    short_term_ttl: timedelta = timedelta(hours=4)
    archive_after: timedelta | None = timedelta(days=30)
    legal_retention: timedelta | None = None
    workspace_retention: timedelta | None = None
    confidence_decay_rate: float = 0.01
    relevance_decay_rate: float = 0.01
    allow_manual_deletion: bool = True
    allow_permanent_deletion: bool = False


@dataclass(frozen=True, slots=True)
class PolicyScope:
    workspace_id: str | None = None
    project_id: str | None = None
    agent_id: str | None = None
    is_enterprise: bool = False
    is_temporary_session: bool = False


@dataclass(frozen=True, slots=True)
class ForgetDecision:
    archive: bool = False
    delete: bool = False
    reason: str = ""


@dataclass(frozen=True, slots=True)
class RetrievalQuery:
    identifier: str | None = None
    conversation_id: str | None = None
    project_id: str | None = None
    context: str | None = None
    intent: str | None = None
    relationship_type: MemoryRelationshipType | None = None
    min_importance: float | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None
    tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class RankingContext:
    project_id: str | None = None
    conversation_id: str | None = None
    workflow_id: str | None = None
    now: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ScoredMemory:
    memory: MemoryRecord
    score: float


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    identifier: str
    occurred_at: datetime
    memory_type: MemoryType
    summary: str
    project_id: str | None
    conversation_id: str | None
