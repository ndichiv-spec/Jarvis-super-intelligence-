from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class TaskState(Enum):
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    @property
    def terminal(self) -> bool:
        return self in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED)

    @property
    def active(self) -> bool:
        return self in (TaskState.RUNNING, TaskState.WAITING)


_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.PLANNED: {TaskState.READY, TaskState.RUNNING, TaskState.CANCELLED},
    TaskState.READY: {TaskState.RUNNING, TaskState.WAITING, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.RUNNING: {TaskState.WAITING, TaskState.BLOCKED, TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.WAITING: {TaskState.READY, TaskState.BLOCKED, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.BLOCKED: {TaskState.READY, TaskState.WAITING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
    TaskState.COMPLETED: set(),
}


class TransitionError(Exception):
    def __init__(self, task_id: str, current: TaskState, target: TaskState) -> None:
        self.task_id = task_id
        self.current = current
        self.target = target
        super().__init__(f"Task {task_id}: cannot transition from {current.value} to {target.value}")


def validate_transition(task_id: str, current: TaskState, target: TaskState) -> None:
    allowed = _TRANSITIONS.get(current, set())
    if target not in allowed:
        raise TransitionError(task_id, current, target)


@dataclass
class StateTransition:
    from_state: TaskState
    to_state: TaskState
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    reason: str = ""


@dataclass
class TaskStateMachine:
    task_id: str
    state: TaskState = TaskState.PLANNED
    history: list[StateTransition] = field(default_factory=list)

    def transition_to(self, target: TaskState, reason: str = "") -> None:
        validate_transition(self.task_id, self.state, target)
        transition = StateTransition(from_state=self.state, to_state=target, reason=reason)
        self.history.append(transition)
        self.state = target

    def can_transition_to(self, target: TaskState) -> bool:
        return target in _TRANSITIONS.get(self.state, set())

    def can_transition_from(self, source: TaskState) -> bool:
        return self.state in _TRANSITIONS.get(source, set())

    @property
    def elapsed_in_state(self) -> float:
        if not self.history:
            return 0.0
        last_transition = self.history[-1]
        return (datetime.now(UTC) - last_transition.timestamp).total_seconds()

    def summary(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "history": [
                {
                    "from": h.from_state.value,
                    "to": h.to_state.value,
                    "timestamp": h.timestamp.isoformat(),
                    "reason": h.reason,
                }
                for h in self.history
            ],
            "elapsed_in_state": self.elapsed_in_state,
        }
