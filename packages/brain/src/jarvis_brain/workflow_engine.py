from __future__ import annotations

from dataclasses import replace
from typing import ClassVar

from jarvis_core import Timestamp

from jarvis_brain.models import (
    BrainExecutionState,
    BrainIssue,
    BrainRequest,
    BrainStage,
    ExecutionMetrics,
    ExecutionTimelineEntry,
    WorkflowStatus,
)


class WorkflowTransitionError(RuntimeError):
    pass


class RuleBasedWorkflowEngine:
    _ALLOWED_TRANSITIONS: ClassVar[dict[WorkflowStatus, tuple[WorkflowStatus, ...]]] = {
        WorkflowStatus.QUEUED: (WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED),
        WorkflowStatus.RUNNING: (
            WorkflowStatus.PAUSED,
            WorkflowStatus.FAILED,
            WorkflowStatus.COMPLETED,
            WorkflowStatus.CANCELLED,
        ),
        WorkflowStatus.PAUSED: (WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED),
        WorkflowStatus.FAILED: (WorkflowStatus.RETRY, WorkflowStatus.ROLLBACK),
        WorkflowStatus.RETRY: (WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED),
        WorkflowStatus.ROLLBACK: (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED),
        WorkflowStatus.CANCELLED: (),
        WorkflowStatus.COMPLETED: (),
    }

    def initialize(self, request: BrainRequest) -> BrainExecutionState:
        created_at = Timestamp.now()
        initial_state = BrainExecutionState(
            execution_id=request.execution_id,
            trace_id=request.trace_id,
            created_at=created_at,
            updated_at=created_at,
            status=WorkflowStatus.QUEUED,
            current_stage=None,
            completed_stages=(),
            errors=(),
            warnings=(),
            metrics=ExecutionMetrics(completed_tasks=0, failed_tasks=0, warning_count=0),
            history=(),
        )
        return self._record(initial_state, details="Execution initialized.")

    def start(self, state: BrainExecutionState) -> BrainExecutionState:
        return self._transition(
            state,
            target_status=WorkflowStatus.RUNNING,
            details="Execution started.",
        )

    def complete_stage(
        self,
        state: BrainExecutionState,
        stage: BrainStage,
        details: str,
    ) -> BrainExecutionState:
        if state.status != WorkflowStatus.RUNNING:
            raise WorkflowTransitionError("Cannot complete stages outside running state.")
        if stage in state.completed_stages:
            return state

        new_state = replace(
            state,
            current_stage=stage,
            completed_stages=(*state.completed_stages, stage),
            metrics=replace(
                state.metrics,
                completed_tasks=state.metrics.completed_tasks + 1,
            ),
            updated_at=Timestamp.now(),
        )
        return self._record(new_state, details=details, stage=stage)

    def fail(
        self,
        state: BrainExecutionState,
        code: str,
        message: str,
        stage: BrainStage | None,
    ) -> BrainExecutionState:
        issue = BrainIssue(code=code, message=message, stage=stage)
        failed_state = self._transition(
            state,
            target_status=WorkflowStatus.FAILED,
            details=f"Execution failed: {message}",
            stage=stage,
        )
        return replace(
            failed_state,
            errors=(*failed_state.errors, issue),
            metrics=replace(
                failed_state.metrics,
                failed_tasks=failed_state.metrics.failed_tasks + 1,
            ),
            updated_at=Timestamp.now(),
        )

    def complete(self, state: BrainExecutionState) -> BrainExecutionState:
        return self._transition(
            state,
            target_status=WorkflowStatus.COMPLETED,
            details="Execution completed.",
        )

    def pause(self, state: BrainExecutionState, details: str) -> BrainExecutionState:
        return self._transition(state, target_status=WorkflowStatus.PAUSED, details=details)

    def cancel(self, state: BrainExecutionState, details: str) -> BrainExecutionState:
        return self._transition(state, target_status=WorkflowStatus.CANCELLED, details=details)

    def retry(self, state: BrainExecutionState, details: str) -> BrainExecutionState:
        return self._transition(state, target_status=WorkflowStatus.RETRY, details=details)

    def rollback(self, state: BrainExecutionState, details: str) -> BrainExecutionState:
        return self._transition(state, target_status=WorkflowStatus.ROLLBACK, details=details)

    def _transition(
        self,
        state: BrainExecutionState,
        *,
        target_status: WorkflowStatus,
        details: str,
        stage: BrainStage | None = None,
    ) -> BrainExecutionState:
        allowed = self._ALLOWED_TRANSITIONS[state.status]
        if target_status not in allowed:
            raise WorkflowTransitionError(
                f"Invalid transition: {state.status.value} -> {target_status.value}"
            )

        transitioned = replace(
            state,
            status=target_status,
            current_stage=stage if stage is not None else state.current_stage,
            updated_at=Timestamp.now(),
        )
        return self._record(transitioned, details=details, stage=stage)

    def _record(
        self,
        state: BrainExecutionState,
        *,
        details: str,
        stage: BrainStage | None = None,
    ) -> BrainExecutionState:
        entry = ExecutionTimelineEntry(
            timestamp=Timestamp.now(),
            status=state.status,
            stage=stage if stage is not None else state.current_stage,
            details=details,
        )
        return replace(
            state,
            history=(*state.history, entry),
            updated_at=entry.timestamp,
        )
