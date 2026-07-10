from dataclasses import dataclass
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier, FileReference


@dataclass(frozen=True, slots=True)
class KnowledgeSource:
    name: str


@dataclass(frozen=True, slots=True)
class Document:
    file: FileReference


@dataclass(frozen=True, slots=True)
class Research:
    summary: str


@dataclass(frozen=True, slots=True)
class Citation:
    reference: str


@dataclass(frozen=True, slots=True)
class KnowledgeCategory:
    name: str


@dataclass(frozen=True, slots=True)
class KnowledgeRelationship:
    target_id: DomainIdentifier
    relation: str


@dataclass(slots=True)
class KnowledgeItem(AggregateRoot):
    source: KnowledgeSource
    document: Document
    research: Research
    citations: tuple[Citation, ...]
    category: KnowledgeCategory
    relationships: tuple[KnowledgeRelationship, ...]


class KnowledgeRepository(Protocol):
    def save(self, item: KnowledgeItem) -> None: ...


@dataclass(frozen=True, slots=True)
class KnowledgeIndexed(DomainEvent):
    category: str
