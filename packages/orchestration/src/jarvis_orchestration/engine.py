from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_orchestration.models import (
    StepStatus,
    Workflow,
    WorkflowExecution,
    WorkflowPriority,
    WorkflowStatus,
    WorkflowStep,
)
from jarvis_orchestration.registry import WorkflowRegistry


class OrchestrationEngine:
    def __init__(self, registry: WorkflowRegistry | None = None) -> None:
        self._registry = registry or WorkflowRegistry()
        self._executions: dict[str, WorkflowExecution] = {}

    def register(self, workflow: Workflow) -> Workflow:
        return self._registry.add(workflow)

    def start(self, workflow_id: str, metadata: dict[str, Any] | None = None) -> WorkflowExecution | None:
        workflow = self._registry.get(workflow_id)
        if workflow is None:
            return None
        execution = WorkflowExecution.create(workflow)
        if metadata:
            execution.metadata.update(metadata)
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now(UTC)
        ready = self._get_ready_steps(workflow, execution)
        for step in ready:
            execution.step_states[step.id] = StepStatus.READY
        self._executions[execution.id] = execution
        return execution

    def advance(self, execution_id: str, step_id: str, success: bool, output: Any = None, error: str | None = None) -> WorkflowExecution | None:
        execution = self._executions.get(execution_id)
        if execution is None or execution.status != WorkflowStatus.RUNNING:
            return None
        workflow = self._registry.get(execution.workflow_id)
        if workflow is None:
            return None

        if success:
            execution.step_states[step_id] = StepStatus.COMPLETED
            execution.step_results[step_id] = output
        else:
            step = next((s for s in workflow.steps if s.id == step_id), None)
            retry_key = f"retry_{step_id}"
            retry_count = execution.metadata.get(retry_key, 0)
            max_retries = step.max_retries if step else 3
            if retry_count < max_retries:
                execution.step_states[step_id] = StepStatus.READY
                execution.metadata[retry_key] = retry_count + 1
            else:
                execution.step_states[step_id] = StepStatus.FAILED
                execution.step_errors[step_id] = error or "Unknown error"

        remaining = [s for s in workflow.steps if execution.step_states.get(s.id) in (StepStatus.PENDING, StepStatus.READY)]
        if not remaining:
            failed = [s for s in workflow.steps if execution.step_states.get(s.id) == StepStatus.FAILED]
            execution.status = WorkflowStatus.FAILED if failed else WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now(UTC)
            if failed:
                execution.error = f"{len(failed)} step(s) failed"
        else:
            for step in self._get_ready_steps(workflow, execution):
                if execution.step_states.get(step.id) == StepStatus.PENDING:
                    execution.step_states[step.id] = StepStatus.READY

        return execution

    def _get_ready_steps(self, workflow: Workflow, execution: WorkflowExecution) -> list[WorkflowStep]:
        ready: list[WorkflowStep] = []
        for step in workflow.steps:
            state = execution.step_states.get(step.id, StepStatus.PENDING)
            if state != StepStatus.PENDING:
                continue
            deps_met = all(
                execution.step_states.get(dep_id) == StepStatus.COMPLETED
                for dep_id in step.depends_on
            )
            if deps_met:
                ready.append(step)
        return ready

    def pause(self, execution_id: str) -> WorkflowExecution | None:
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.PAUSED
        return execution

    def resume(self, execution_id: str) -> WorkflowExecution | None:
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.PAUSED:
            execution.status = WorkflowStatus.RUNNING
        return execution

    def cancel(self, execution_id: str) -> WorkflowExecution | None:
        execution = self._executions.get(execution_id)
        if execution and execution.status in (WorkflowStatus.RUNNING, WorkflowStatus.PAUSED, WorkflowStatus.PENDING):
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now(UTC)
        return execution

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        return self._executions.get(execution_id)

    def list_executions(self, workflow_id: str | None = None) -> list[WorkflowExecution]:
        execs = list(self._executions.values())
        if workflow_id:
            execs = [e for e in execs if e.workflow_id == workflow_id]
        return sorted(execs, key=lambda e: e.started_at or datetime.min, reverse=True)

    @property
    def registry(self) -> WorkflowRegistry:
        return self._registry
