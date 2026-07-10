from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Protocol

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class AuditEventType(Enum):
    AUTHENTICATION = auto()
    AUTHORIZATION = auto()
    POLICY_DECISION = auto()
    WORKFLOW_EXECUTION = auto()
    TOOL_USAGE = auto()
    AGENT_ACTIVITY = auto()
    EXTENSION_LIFECYCLE = auto()
    CONFIGURATION_CHANGE = auto()


@dataclass(frozen=True, slots=True)
class AuditField:
    key: str
    value: str

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("key cannot be empty")


@dataclass(frozen=True, slots=True)
class AuditEvent:
    metadata: SecurityMetadata
    event_type: AuditEventType
    actor_identifier: str
    target_identifier: str | None
    occurred_at: datetime
    summary: str
    details: tuple[AuditField, ...] = ()

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.AUDIT_EVENT:
            raise ValueError("metadata.object_type must be audit_event")
        if not self.actor_identifier.strip():
            raise ValueError("actor_identifier cannot be empty")
        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        event_type: AuditEventType,
        actor_identifier: str,
        owner_identifier: str,
        summary: str,
        target_identifier: str | None = None,
        details: tuple[AuditField, ...] = (),
        workspace_identifier: str | None = None,
        organization_identifier: str | None = None,
    ) -> AuditEvent:
        event_time = datetime.now(tz=UTC)
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.AUDIT_EVENT,
                owner_identifier=owner_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            event_type=event_type,
            actor_identifier=actor_identifier,
            target_identifier=target_identifier,
            occurred_at=event_time,
            summary=summary,
            details=details,
        )


class AuditSinkContract(Protocol):
    def record(self, event: AuditEvent) -> None:
        ...

    def list_events(self, event_type: AuditEventType | None = None) -> tuple[AuditEvent, ...]:
        ...


@dataclass(slots=True)
class InMemoryAuditSink(AuditSinkContract):
    _events: list[AuditEvent] = field(default_factory=list)

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)

    def list_events(self, event_type: AuditEventType | None = None) -> tuple[AuditEvent, ...]:
        if event_type is None:
            return tuple(self._events)
        return tuple(event for event in self._events if event.event_type is event_type)
