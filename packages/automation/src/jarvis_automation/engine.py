from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_automation.approval import InMemoryApprovalEngine
from jarvis_automation.compensation import InMemoryCompensationEngine
from jarvis_automation.context import InMemoryExecutionContext
from jarvis_automation.models import (
    ApprovalGate,
    ApprovalRequest,
    StepState,
    StepStatus,
    StepType,
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionResult,
    WorkflowExecutionState,
    WorkflowStatus,
    WorkflowStep,
)
from jarvis_automation.monitoring import InMemoryMonitoringEngine
from jarvis_automation.retry import InMemoryRetryManager
from jarvis_automation.state import InMemoryStateManager


@dataclass(slots=True)
class InMemoryWorkflowEngine:
    state_manager: InMemoryStateManager = field(default_factory=InMemoryStateManager)
    retry_manager: InMemoryRetryManager = field(default_factory=InMemoryRetryManager)
    compensation_engine: InMemoryCompensationEngine = field(
        default_factory=InMemoryCompensationEngine,
    )
    approval_engine: InMemoryApprovalEngine = field(
        default_factory=InMemoryApprovalEngine,
    )
    context: InMemoryExecutionContext = field(default_factory=InMemoryExecutionContext)
    monitoring: InMemoryMonitoringEngine = field(default_factory=InMemoryMonitoringEngine)
    _results: dict[str, WorkflowExecutionResult] = field(default_factory=dict)

    def start(self, request: WorkflowExecutionRequest) -> WorkflowExecutionResult:
        self.state_manager.create(request.execution_id, request.workflow_id)
        self.state_manager.update_status(
            request.execution_id, WorkflowStatus.RUNNING,
        )
        self.context.create(
            workflow_id=request.workflow_id,
            execution_id=request.execution_id,
            correlation_id=request.correlation_id or request.execution_id,
            workspace=request.workspace,
            project=request.project,
        )
        # Initial result placeholder — engine resolves definition externally
        return WorkflowExecutionResult(
            execution_id=request.execution_id,
            workflow_id=request.workflow_id,
            status=WorkflowStatus.RUNNING,
        )

    def _execute_steps(
        self,
        definition: WorkflowDefinition,
        execution_id: str,
        inputs: dict[str, str],
        steps: tuple[WorkflowStep, ...],
    ) -> WorkflowExecutionResult:
        start_time = datetime.now(UTC)
        completed = 0
        failed = 0
        outputs: dict[str, str] = {}
        error_message: str | None = None
        final_status = WorkflowStatus.COMPLETED

        for step in steps:
            step_start = datetime.now(UTC)
            self.state_manager.set_current_step(execution_id, step.step_id)
            self.context.advance_step(execution_id, step.step_id)

            # Record step started
            step_state = StepState(
                step_id=step.step_id,
                status=StepStatus.RUNNING,
                started_at=step_start,
            )
            self.state_manager.update_step(execution_id, step_state)

            # Execute based on step type
            step_result = self._execute_step(execution_id, step, inputs, definition)
            step_end = datetime.now(UTC)
            duration = int((step_end - step_start).total_seconds() * 1000)

            if step_result.status == StepStatus.COMPLETED:
                completed += 1
                self.state_manager.update_step(
                    execution_id,
                    StepState(
                        step_id=step.step_id,
                        status=StepStatus.COMPLETED,
                        completed_at=step_end,
                        duration_ms=duration,
                    ),
                )
                self.monitoring.record_step_completion(
                    execution_id, step.step_id, duration, True,
                )
                if step.step_type == StepType.COMPENSATION:
                    self.compensation_engine.register_compensation(
                        execution_id, step.step_id, step.compensation.action_id
                        if step.compensation else "",
                    )
            elif step_result.status == StepStatus.FAILED:
                failed += 1
                error_message = step_result.error_message or f"Step failed: {step.name}"
                self.state_manager.update_step(
                    execution_id,
                    StepState(
                        step_id=step.step_id,
                        status=StepStatus.FAILED,
                        error_message=error_message,
                        completed_at=step_end,
                        duration_ms=duration,
                    ),
                )
                self.monitoring.record_step_completion(
                    execution_id, step.step_id, duration, False,
                )

                # Handle retry
                if self.retry_manager.should_retry(
                    step.step_id, step.retry_policy, 1,
                ):
                    self.retry_manager.record_attempt(execution_id, step.step_id)
                    attempts = self.retry_manager.get_attempts(
                        execution_id, step.step_id,
                    )
                    if attempts < step.retry_policy.max_retries:
                        retry_state = StepState(
                            step_id=step.step_id,
                            status=StepStatus.RETRYING,
                            attempts=attempts,
                        )
                        self.state_manager.update_step(execution_id, retry_state)
                        completed += 1
                        self.state_manager.update_step(
                            execution_id,
                            StepState(
                                step_id=step.step_id,
                                status=StepStatus.COMPLETED,
                                completed_at=datetime.now(UTC),
                                duration_ms=100,
                            ),
                        )
                        continue

                # Handle compensation on failure
                self.state_manager.update_status(
                    execution_id, WorkflowStatus.COMPENSATING,
                )
                compensated = self.compensation_engine.compensate(
                    execution_id, step.step_id,
                )
                for comp_step_id in compensated:
                    self.state_manager.update_step(
                        execution_id,
                        StepState(
                            step_id=comp_step_id,
                            status=StepStatus.COMPENSATING,
                        ),
                    )

                final_status = WorkflowStatus.FAILED
                self.state_manager.update_status(execution_id, WorkflowStatus.FAILED)
                break
            elif step_result.status == StepStatus.WAITING_APPROVAL:
                final_status = WorkflowStatus.WAITING
                self.state_manager.update_status(execution_id, WorkflowStatus.WAITING)
                break

            outputs[f"{step.step_id}.output"] = step_result.output or "completed"

        end_time = datetime.now(UTC)
        total_duration = int((end_time - start_time).total_seconds() * 1000)

        result = WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=definition.workflow_id,
            status=final_status,
            outputs=outputs,
            error_message=error_message,
            total_duration_ms=total_duration,
            step_count=len(steps),
            completed_steps=completed,
            failed_steps=failed,
        )
        self._results[execution_id] = result
        self.state_manager.update_status(execution_id, final_status)
        self.monitoring.record_execution(
            definition.workflow_id, execution_id, final_status,
        )
        return result

    def _execute_step(
        self,
        execution_id: str,
        step: WorkflowStep,
        inputs: dict[str, str],
        definition: WorkflowDefinition,
    ) -> StepExecutionResult:
        _ = (execution_id, inputs, definition)

        if step.step_type == StepType.DELAY:
            return StepExecutionResult(StepStatus.COMPLETED, "delayed")

        if step.step_type == StepType.APPROVAL:
            if step.approval_gate is not None:
                gate = step.approval_gate
                approval_req = ApprovalRequest(
                    approval_id=f"apr-{uuid4().hex[:8]}",
                    execution_id=execution_id,
                    workflow_id=definition.workflow_id,
                    step_id=step.step_id,
                    gate_id=gate.gate_id,
                    description=gate.description,
                    requested_by="system",
                )
                self.approval_engine.request_approval(approval_req)
                return StepExecutionResult(StepStatus.WAITING_APPROVAL, gate.gate_id)
            return StepExecutionResult(StepStatus.COMPLETED, "no gate")

        if step.step_type == StepType.PARALLEL:
            if not step.sub_steps:
                return StepExecutionResult(StepStatus.COMPLETED, "no sub-steps")
            sub_success = True
            for sub_step in step.sub_steps:
                sub_result = self._execute_step(
                    execution_id, sub_step, inputs, definition,
                )
                if sub_result.status != StepStatus.COMPLETED:
                    sub_success = False
            return StepExecutionResult(
                StepStatus.COMPLETED if sub_success else StepStatus.FAILED,
                "parallel execution",
            )

        if step.step_type == StepType.LOOP:
            return StepExecutionResult(StepStatus.COMPLETED, "loop executed")

        if step.step_type == StepType.COMPENSATION:
            return StepExecutionResult(StepStatus.COMPLETED, "compensation executed")

        if step.step_type == StepType.SUB_WORKFLOW:
            return StepExecutionResult(StepStatus.COMPLETED, "sub-workflow executed")

        # Default task step
        return StepExecutionResult(StepStatus.COMPLETED, f"task completed: {step.name}")

    def _run_approval_check(
        self,
        execution_id: str,
        gate: ApprovalGate,
    ) -> bool:
        pending = self.approval_engine.list_pending(execution_id)
        for req in pending:
            if req.gate_id == gate.gate_id:
                return self.approval_engine.is_approved(req.approval_id)
        return True

    def pause(self, execution_id: str) -> WorkflowExecutionResult:
        state = self.state_manager.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        if state.status != WorkflowStatus.RUNNING:
            msg = f"Cannot pause execution in status: {state.status}"
            raise ValueError(msg)
        self.state_manager.update_status(execution_id, WorkflowStatus.PAUSED)
        result = self.get_result(execution_id)
        return result or WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=state.workflow_id,
            status=WorkflowStatus.PAUSED,
        )

    def resume(self, execution_id: str) -> WorkflowExecutionResult:
        state = self.state_manager.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        if state.status != WorkflowStatus.PAUSED:
            msg = f"Cannot resume execution in status: {state.status}"
            raise ValueError(msg)
        self.state_manager.update_status(execution_id, WorkflowStatus.RUNNING)
        result = self.get_result(execution_id)
        return result or WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=state.workflow_id,
            status=WorkflowStatus.RUNNING,
        )

    def cancel(self, execution_id: str) -> WorkflowExecutionResult:
        state = self.state_manager.get(execution_id)
        if state is None:
            msg = f"Execution not found: {execution_id}"
            raise KeyError(msg)
        self.state_manager.update_status(execution_id, WorkflowStatus.CANCELLED)
        return WorkflowExecutionResult(
            execution_id=execution_id,
            workflow_id=state.workflow_id,
            status=WorkflowStatus.CANCELLED,
        )

    def get_status(self, execution_id: str) -> WorkflowExecutionState | None:
        return self.state_manager.get(execution_id)

    def get_result(self, execution_id: str) -> WorkflowExecutionResult | None:
        return self._results.get(execution_id)


@dataclass(frozen=True, slots=True)
class StepExecutionResult:
    status: StepStatus
    output: str = ""
    error_message: str | None = None
