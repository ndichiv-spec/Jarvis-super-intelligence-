from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import PriorityLevel


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"


@dataclass(frozen=True, slots=True)
class Channel:
    name: str


@dataclass(slots=True)
class Notification(AggregateRoot):
    channel: Channel
    priority: PriorityLevel
    status: NotificationStatus
    content: str


class DeliveryPort(Protocol):
    def deliver(self, notification: Notification) -> None: ...


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None: ...


@dataclass(frozen=True, slots=True)
class NotificationSent(DomainEvent):
    channel_name: str
