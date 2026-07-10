from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier, ImportanceLevel


class MemoryType(StrEnum):
    FACT = "fact"
    EPISODIC = "episodic"


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    days: int


@dataclass(frozen=True, slots=True)
class MemoryRelationship:
    target_id: DomainIdentifier
    relation: str


@dataclass(frozen=True, slots=True)
class MemoryMetadata:
    source: str


@dataclass(frozen=True, slots=True)
class MemoryReference:
    key: str


@dataclass(slots=True)
class MemoryEntry(AggregateRoot):
    memory_type: MemoryType
    content: str
    importance: ImportanceLevel
    retention_policy: RetentionPolicy
    relationships: tuple[MemoryRelationship, ...]
    metadata: MemoryMetadata
    references: tuple[MemoryReference, ...]


class MemoryRepository(Protocol):
    def save(self, memory: MemoryEntry) -> None: ...


@dataclass(frozen=True, slots=True)
class MemoryStored(DomainEvent):
    memory_type: MemoryType
