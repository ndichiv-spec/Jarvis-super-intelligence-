from dataclasses import dataclass

from jarvis_core.domain.shared.value_objects import DomainIdentifier, Timestamp


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: DomainIdentifier
    occurred_at: Timestamp
    aggregate_id: DomainIdentifier
