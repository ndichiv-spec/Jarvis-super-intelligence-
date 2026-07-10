from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier, FileReference, Timestamp


class ConversationState(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class Attachment:
    file: FileReference


@dataclass(frozen=True, slots=True)
class Message:
    id: DomainIdentifier
    author_id: DomainIdentifier
    content: str
    attachments: tuple[Attachment, ...]
    created_at: Timestamp


@dataclass(frozen=True, slots=True)
class ConversationContext:
    summary: str


@dataclass(frozen=True, slots=True)
class ConversationMetadata:
    topic: str
    tags: tuple[str, ...]


@dataclass(slots=True)
class Conversation(AggregateRoot):
    context: ConversationContext
    history: tuple[Message, ...]
    metadata: ConversationMetadata
    state: ConversationState


class ConversationRepository(Protocol):
    def save(self, conversation: Conversation) -> None: ...

    def get(self, conversation_id: DomainIdentifier) -> Conversation | None: ...


@dataclass(frozen=True, slots=True)
class ConversationStarted(DomainEvent):
    initiator_id: DomainIdentifier


@dataclass(frozen=True, slots=True)
class ConversationEnded(DomainEvent):
    reason: str
