from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier


class ExecutionState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Trigger:
    name: str


@dataclass(frozen=True, slots=True)
class Condition:
    expression: str


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    name: str
    condition: Condition


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    summary: str


@dataclass(slots=True)
class Workflow(AggregateRoot):
    trigger: Trigger
    steps: tuple[WorkflowStep, ...]
    execution_state: ExecutionState
    result: WorkflowResult | None


class SchedulePort(Protocol):
    def schedule(self, workflow_id: DomainIdentifier) -> None: ...


class WorkflowRepository(Protocol):
    def save(self, workflow: Workflow) -> None: ...


@dataclass(frozen=True, slots=True)
class WorkflowExecuted(DomainEvent):
    status: ExecutionState
