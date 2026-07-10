from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any
from uuid import uuid4


class ChannelType(StrEnum):
    INTERNAL = "internal"
    AI_CONVERSATION = "ai_conversation"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"
    WEBSOCKET = "websocket"
    SYSTEM = "system"
    EXTERNAL = "external"


class MessageType(StrEnum):
    TEXT = "text"
    COMMAND = "command"
    EVENT = "event"
    NOTIFICATION = "notification"
    SYSTEM = "system"
    ERROR = "error"
    WARNING = "warning"


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ReadStatus(StrEnum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class NotificationLevel(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MeetingStatus(StrEnum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    IDLE = "idle"
    AWAY = "away"
    CLOSED = "closed"


class PresenceStatus(StrEnum):
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"
    DO_NOT_DISTURB = "do_not_disturb"


class SubscriptionType(StrEnum):
    CHANNEL = "channel"
    CONVERSATION = "conversation"
    TOPIC = "topic"
    USER = "user"
    AGENT = "agent"


def _freeze_mapping(values: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(values))


@dataclass(frozen=True, slots=True)
class Attachment:
    attachment_id: str = field(default_factory=lambda: uuid4().hex)
    filename: str = ""
    content_type: str = "application/octet-stream"
    size: int = 0
    storage_path: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class CommunicationMessage:
    message_id: str = field(default_factory=lambda: uuid4().hex)
    sender: str = ""
    receiver: str = ""
    channel: ChannelType = ChannelType.INTERNAL
    conversation_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    message_type: MessageType = MessageType.TEXT
    priority: Priority = Priority.NORMAL
    body: str = ""
    subject: str | None = None
    attachments: tuple[Attachment, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    read_status: ReadStatus = ReadStatus.UNREAD

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Conversation:
    conversation_id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    participants: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Mapping[str, Any] = field(default_factory=dict)
    is_archived: bool = False
    message_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Notification:
    notification_id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    body: str = ""
    level: NotificationLevel = NotificationLevel.INFO
    source: str = ""
    target_user: str | None = None
    target_channel: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    read: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)
    action_url: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Channel:
    channel_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    channel_type: ChannelType = ChannelType.INTERNAL
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    members: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    is_active: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Session:
    session_id: str = field(default_factory=lambda: uuid4().hex)
    user_id: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Mapping[str, Any] = field(default_factory=dict)
    client_info: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class PresenceInfo:
    user_id: str = ""
    status: PresenceStatus = PresenceStatus.OFFLINE
    last_seen: datetime | None = None
    current_activity: str = ""
    connected_clients: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Meeting:
    meeting_id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    organizer: str = ""
    participants: tuple[str, ...] = ()
    status: MeetingStatus = MeetingStatus.SCHEDULED
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    transcript: str = ""
    summary: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class Subscription:
    subscription_id: str = field(default_factory=lambda: uuid4().hex)
    subscriber_id: str = ""
    subscription_type: SubscriptionType = SubscriptionType.CHANNEL
    target_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    active: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class DeliveryReceipt:
    message_id: str = ""
    recipient: str = ""
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    status: DeliveryStatus = DeliveryStatus.PENDING
    error: str | None = None


@dataclass(frozen=True, slots=True)
class StreamChunk:
    stream_id: str = ""
    sequence: int = 0
    data: str = ""
    chunk_type: str = "data"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class AuditEntry:
    entry_id: str = field(default_factory=lambda: uuid4().hex)
    action: str = ""
    actor: str = ""
    target: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: Mapping[str, Any] = field(default_factory=dict)
    success: bool = True
    ip_address: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", _freeze_mapping(self.details))


@dataclass(frozen=True, slots=True)
class AnalyticsEvent:
    event_id: str = field(default_factory=lambda: uuid4().hex)
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: Mapping[str, Any] = field(default_factory=dict)
    source: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", _freeze_mapping(self.data))
