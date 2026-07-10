from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class WorkflowPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    id: str
    name: str
    description: str = ""
    depends_on: tuple[str, ...] = ()
    timeout_seconds: float | None = None
    required_capabilities: tuple[str, ...] = ()
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, name: str, *, description: str = "", depends_on: tuple[str, ...] | None = None,
               timeout_seconds: float | None = None, required_capabilities: tuple[str, ...] | None = None,
               max_retries: int = 3) -> WorkflowStep:
        return cls(
            id=f"step-{uuid4().hex[:12]}",
            name=name,
            description=description,
            depends_on=depends_on or (),
            timeout_seconds=timeout_seconds,
            required_capabilities=required_capabilities or (),
            max_retries=max_retries,
        )


@dataclass(frozen=True, slots=True)
class Workflow:
    id: str
    name: str
    description: str = ""
    steps: tuple[WorkflowStep, ...] = ()
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    owner: str = "system"
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, name: str, *, description: str = "", priority: WorkflowPriority = WorkflowPriority.MEDIUM,
               owner: str = "system", tags: tuple[str, ...] | None = None,
               steps: tuple[WorkflowStep, ...] | None = None) -> Workflow:
        return cls(
            id=f"wf-{uuid4().hex[:12]}",
            name=name,
            description=description,
            priority=priority,
            owner=owner,
            tags=tags or (),
            steps=steps or (),
        )


@dataclass
class WorkflowExecution:
    id: str
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    step_states: dict[str, StepStatus] = field(default_factory=dict)
    step_results: dict[str, Any] = field(default_factory=dict)
    step_errors: dict[str, str] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, workflow: Workflow) -> WorkflowExecution:
        return cls(
            id=f"exec-{uuid4().hex[:12]}",
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            step_states={s.id: StepStatus.PENDING for s in workflow.steps},
        )
