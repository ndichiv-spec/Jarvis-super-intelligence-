from dataclasses import dataclass, field

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.value_objects import DomainIdentifier


@dataclass(slots=True)
class Entity:
    id: DomainIdentifier


@dataclass(slots=True)
class AggregateRoot(Entity):
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
