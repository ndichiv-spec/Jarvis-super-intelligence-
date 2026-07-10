from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_tools.models import (
    ExecutionStatus,
    ToolDefinition,
    ToolExecutionPolicy,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolSchema,
)


@dataclass(slots=True)
class InMemoryToolExecutor:
    _results: dict[str, ToolExecutionResult] = field(default_factory=dict)

    def can_execute(self, identifier: str) -> bool:
        _ = identifier
        return True

    def execute(
        self,
        definition: ToolDefinition,
        params: dict[str, str],
    ) -> ToolExecutionResult:
        start = datetime.now(UTC)
        mock_output = f"Executed {definition.identifier} with " f"{len(params)} parameter(s)"
        duration = int(
            (datetime.now(UTC) - start).total_seconds() * 1000,
        )
        return ToolExecutionResult(
            request_id=f"exec-{uuid4().hex[:8]}",
            status=ExecutionStatus.COMPLETED,
            output=mock_output,
            execution_time_ms=max(duration, 1),
        )


@dataclass(slots=True)
class InMemoryExecutionEngine:
    _executors: dict[str, InMemoryToolExecutor] = field(default_factory=dict)
    _requests: dict[str, ToolExecutionRequest] = field(default_factory=dict)
    _results: dict[str, ToolExecutionResult] = field(default_factory=dict)
    _statuses: dict[str, ExecutionStatus] = field(default_factory=dict)

    def register_executor(
        self,
        tool_identifier: str,
        executor: InMemoryToolExecutor,
    ) -> None:
        self._executors[tool_identifier] = executor

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self._requests[request.request_id] = request
        self._statuses[request.request_id] = ExecutionStatus.QUEUED
        self._statuses[request.request_id] = ExecutionStatus.RUNNING

        executor = self._executors.get(request.tool_identifier)
        if executor is None:
            result = ToolExecutionResult(
                request_id=request.request_id,
                status=ExecutionStatus.FAILED,
                output="",
                error_message=f"No executor for tool: {request.tool_identifier}",
            )
            self._results[request.request_id] = result
            self._statuses[request.request_id] = ExecutionStatus.FAILED
            return result

        stub_def = ToolDefinition(
            identifier=request.tool_identifier,
            name=request.tool_identifier,
            description="",
            version="0.1.0",
            category="utility",  # type: ignore[arg-type]
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
            execution_policy=ToolExecutionPolicy(),
        )
        result = executor.execute(stub_def, request.parameters)
        stored = ToolExecutionResult(
            request_id=request.request_id,
            status=result.status,
            output=result.output,
            error_message=result.error_message,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata,
        )
        self._results[request.request_id] = stored
        self._statuses[request.request_id] = stored.status
        return stored

    def get_status(self, request_id: str) -> ExecutionStatus | None:
        return self._statuses.get(request_id)

    def get_result(self, request_id: str) -> ToolExecutionResult | None:
        return self._results.get(request_id)

    def cancel(self, request_id: str) -> None:
        if request_id in self._statuses:
            if self._statuses[request_id] in (
                ExecutionStatus.QUEUED,
                ExecutionStatus.RUNNING,
                ExecutionStatus.RETRY_REQUESTED,
            ):
                self._statuses[request_id] = ExecutionStatus.CANCELLED
                result = self._results.get(request_id)
                if result is not None:
                    self._results[request_id] = ToolExecutionResult(
                        request_id=request_id,
                        status=ExecutionStatus.CANCELLED,
                        output=result.output,
                        error_message="Cancelled by user",
                        execution_time_ms=result.execution_time_ms,
                    )

    def list_active(self) -> tuple[ToolExecutionRequest, ...]:
        active_statuses = {
            ExecutionStatus.QUEUED,
            ExecutionStatus.RUNNING,
            ExecutionStatus.RETRY_REQUESTED,
        }
        return tuple(
            req
            for req in self._requests.values()
            if self._statuses.get(req.request_id) in active_statuses
        )
