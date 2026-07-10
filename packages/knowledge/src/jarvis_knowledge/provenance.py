from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


class ProvenanceEventType:
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    IMPORTED = "imported"
    TRANSFORMED = "transformed"
    CLASSIFIED = "classified"
    VALIDATED = "validated"
    INDEXED = "indexed"
    SYNCED = "synced"


@dataclass(frozen=True, slots=True)
class ProvenanceEvent:
    event_id: str
    document_id: str
    event_type: str
    timestamp: datetime
    actor: str
    description: str = ""
    previous_state: str | None = None
    new_state: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ProvenanceLog:
    _events: dict[str, list[ProvenanceEvent]] = field(default_factory=dict)

    def record(self, event: ProvenanceEvent) -> None:
        if event.document_id not in self._events:
            self._events[event.document_id] = []
        self._events[event.document_id].append(event)

    def history(self, document_id: str) -> tuple[ProvenanceEvent, ...]:
        return tuple(self._events.get(document_id, []))

    def events_by_type(self, event_type: str) -> tuple[ProvenanceEvent, ...]:
        all_events: list[ProvenanceEvent] = []
        for events in self._events.values():
            for e in events:
                if e.event_type == event_type:
                    all_events.append(e)
        return tuple(all_events)

    def events_by_actor(self, actor: str) -> tuple[ProvenanceEvent, ...]:
        all_events: list[ProvenanceEvent] = []
        for events in self._events.values():
            for e in events:
                if e.actor == actor:
                    all_events.append(e)
        return tuple(all_events)

    def clear(self) -> None:
        self._events.clear()


class ProvenanceTracker(Protocol):
    def track(
        self,
        document_id: str,
        event_type: str,
        actor: str,
        *,
        description: str = "",
        previous_state: str | None = None,
        new_state: str | None = None,
    ) -> ProvenanceEvent: ...
    def history(self, document_id: str) -> tuple[ProvenanceEvent, ...]: ...


class DefaultProvenanceTracker:
    def __init__(self, log: ProvenanceLog | None = None) -> None:
        self._log = log or ProvenanceLog()
        from uuid import uuid4
        self._uuid4 = uuid4

    @property
    def log(self) -> ProvenanceLog:
        return self._log

    def track(
        self,
        document_id: str,
        event_type: str,
        actor: str,
        *,
        description: str = "",
        previous_state: str | None = None,
        new_state: str | None = None,
    ) -> ProvenanceEvent:
        event = ProvenanceEvent(
            event_id=f"evt-{self._uuid4().hex[:12]}",
            document_id=document_id,
            event_type=event_type,
            timestamp=datetime.now(UTC),
            actor=actor,
            description=description,
            previous_state=previous_state,
            new_state=new_state,
        )
        self._log.record(event)
        return event

    def history(self, document_id: str) -> tuple[ProvenanceEvent, ...]:
        return self._log.history(document_id)
