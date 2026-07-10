"""Lifecycle Manager — state machine for platform lifecycle transitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class LifecycleState(StrEnum):
    created = "created"
    initializing = "initializing"
    starting = "starting"
    ready = "ready"
    degraded = "degraded"
    stopping = "stopping"
    stopped = "stopped"
    failed = "failed"


_VALID_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.created: {LifecycleState.initializing, LifecycleState.failed},
    LifecycleState.initializing: {LifecycleState.starting, LifecycleState.failed},
    LifecycleState.starting: {LifecycleState.ready, LifecycleState.degraded, LifecycleState.stopping, LifecycleState.failed},
    LifecycleState.ready: {LifecycleState.stopping, LifecycleState.degraded, LifecycleState.failed},
    LifecycleState.degraded: {LifecycleState.ready, LifecycleState.stopping, LifecycleState.failed},
    LifecycleState.stopping: {LifecycleState.stopped, LifecycleState.failed},
    LifecycleState.stopped: set(),
    LifecycleState.failed: {LifecycleState.stopping},
}


@dataclass(frozen=True, slots=True)
class LifecycleEvent:
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    reason: str = ""


class LifecycleError(Exception):
    def __init__(self, from_state: LifecycleState, to_state: LifecycleState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(f"Cannot transition from {from_state.value} to {to_state.value}")


class LifecycleManager:
    def __init__(self) -> None:
        self._state: LifecycleState = LifecycleState.created
        self._history: list[LifecycleEvent] = []

    @property
    def state(self) -> LifecycleState:
        return self._state

    @property
    def history(self) -> list[LifecycleEvent]:
        return list(self._history)

    def transition(self, target: LifecycleState, reason: str = "") -> LifecycleState:
        if target not in _VALID_TRANSITIONS.get(self._state, set()):
            raise LifecycleError(self._state, target)
        event = LifecycleEvent(from_state=self._state, to_state=target, reason=reason)
        self._history.append(event)
        self._state = target
        return self._state

    def can_transition_to(self, target: LifecycleState) -> bool:
        return target in _VALID_TRANSITIONS.get(self._state, set())

    def elapsed_in_state(self) -> float:
        if not self._history:
            return 0.0
        latest = self._history[-1]
        return (datetime.now(UTC) - latest.timestamp).total_seconds()
