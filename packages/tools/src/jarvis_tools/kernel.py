from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_tools.definitions import BUILT_IN_TOOLS
from jarvis_tools.discovery import InMemoryDiscoveryEngine
from jarvis_tools.execution import InMemoryExecutionEngine, InMemoryToolExecutor
from jarvis_tools.health import InMemoryHealthMonitor
from jarvis_tools.models import (
    ExecutionStatus,
    ToolDefinition,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolHealthReport,
    ToolMetadata,
    ToolValidationReport,
)
from jarvis_tools.permissions import InMemoryPermissionManager
from jarvis_tools.policy import InMemoryPolicyEngine
from jarvis_tools.registry import InMemoryToolRegistry
from jarvis_tools.validation import InMemoryValidationEngine


@dataclass(slots=True)
class ToolKernel:
    registry: InMemoryToolRegistry = field(default_factory=InMemoryToolRegistry)
    discovery: InMemoryDiscoveryEngine = field(default_factory=InMemoryDiscoveryEngine)
    validation: InMemoryValidationEngine = field(default_factory=InMemoryValidationEngine)
    execution: InMemoryExecutionEngine = field(default_factory=InMemoryExecutionEngine)
    permissions: InMemoryPermissionManager = field(default_factory=InMemoryPermissionManager)
    policy: InMemoryPolicyEngine = field(default_factory=InMemoryPolicyEngine)
    health: InMemoryHealthMonitor = field(default_factory=InMemoryHealthMonitor)

    def __post_init__(self) -> None:
        self._register_builtins()
        self.discovery.sync(self.registry.list())

    def _register_builtins(self) -> None:
        for definition in BUILT_IN_TOOLS:
            self.registry.register(definition)
            default_executor = InMemoryToolExecutor()
            self.execution.register_executor(
                definition.identifier,
                default_executor,
            )

    def register(self, definition: ToolDefinition) -> ToolMetadata:
        meta = self.registry.register(definition)
        self.discovery.sync(self.registry.list())
        default_executor = InMemoryToolExecutor()
        self.execution.register_executor(definition.identifier, default_executor)
        return meta

    def update(self, metadata: ToolMetadata) -> None:
        self.registry.update(metadata)
        self.discovery.sync(self.registry.list())

    def deregister(self, identifier: str) -> None:
        self.registry.deregister(identifier)
        self.discovery.sync(self.registry.list())

    def validate(
        self,
        definition: ToolDefinition,
        parameters: dict[str, str],
        agent_id: str = "system",
        workspace: str = "*",
    ) -> ToolValidationReport:
        return self.validation.validate_all(
            definition,
            parameters,
            agent_id,
            workspace,
        )

    def execute(
        self,
        tool_identifier: str,
        parameters: dict[str, str],
        agent_id: str = "system",
        workspace: str = "*",
    ) -> ToolExecutionResult:
        metadata = self.registry.get(tool_identifier)
        if metadata is None:
            return ToolExecutionResult(
                request_id=f"req-{uuid4().hex[:8]}",
                status=ExecutionStatus.FAILED,
                output="",
                error_message=f"Tool not found: {tool_identifier}",
            )

        definition = metadata.definition

        # Validate before execution
        report = self.validation.validate_all(
            definition,
            parameters,
            agent_id,
            workspace,
        )
        if not report.valid:
            return ToolExecutionResult(
                request_id=f"req-{uuid4().hex[:8]}",
                status=ExecutionStatus.FAILED,
                output="",
                error_message="; ".join(report.errors),
            )

        request = ToolExecutionRequest(
            request_id=f"req-{uuid4().hex[:8]}",
            tool_identifier=tool_identifier,
            agent_id=agent_id,
            parameters=parameters,
            workspace=workspace,
        )
        result = self.execution.execute(request)
        self.health.record_execution(
            tool_identifier,
            result.execution_time_ms,
            result.status == ExecutionStatus.COMPLETED,
        )
        return result

    def get_health(self, tool_identifier: str) -> ToolHealthReport | None:
        return self.health.get_report(tool_identifier)

    def search_tools(self, query: str) -> tuple[ToolDefinition, ...]:
        return self.discovery.search(query)

    def list_tools(self) -> tuple[ToolMetadata, ...]:
        return self.registry.list()
