from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_automation.models import (
    StepState,
    WorkflowExecutionState,
    WorkflowStatus,
)


@dataclass(slots=True)
class InMemoryStateManager:
    _states: dict[str, WorkflowExecutionState] = field(default_factory=dict)

    def create(self, execution_id: str, workflow_id: str) -> WorkflowExecutionState:
        state = WorkflowExecutionState(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.CREATED,
            started_at=datetime.now(UTC),
        )
        self._states[execution_id] = state
        return state

    def get(self, execution_id: str) -> WorkflowExecutionState | None:
        return self._states.get(execution_id)

    def update_status(
        self, execution_id: str, status: WorkflowStatus,
    ) -> WorkflowExecutionState:
        state = self._states.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        updated = state.with_status(status)
        if status in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
            WorkflowStatus.ARCHIVED,
        ):
            updated = WorkflowExecutionState(
                execution_id=updated.execution_id,
                workflow_id=updated.workflow_id,
                status=updated.status,
                current_step_id=updated.current_step_id,
                step_states=updated.step_states,
                error_message=updated.error_message,
                started_at=updated.started_at,
                completed_at=datetime.now(UTC),
            )
        self._states[execution_id] = updated
        return updated

    def update_step(
        self, execution_id: str, step_state: StepState,
    ) -> WorkflowExecutionState:
        state = self._states.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        updated = state.with_step_state(step_state)
        self._states[execution_id] = updated
        return updated

    def set_current_step(
        self, execution_id: str, step_id: str,
    ) -> WorkflowExecutionState:
        state = self._states.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        updated = state.with_current_step(step_id)
        self._states[execution_id] = updated
        return updated

    def list_by_status(self, status: WorkflowStatus) -> tuple[WorkflowExecutionState, ...]:
        return tuple(s for s in self._states.values() if s.status == status)
