from __future__ import annotations

from typing import Protocol

from jarvis_tools.models import (
    ExecutionStatus,
    ToolCapability,
    ToolCategory,
    ToolDefinition,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolHealthReport,
    ToolMetadata,
    ToolPermission,
    ToolPolicy,
    ToolPolicyScope,
    ToolStatus,
    ToolValidationReport,
)


class ToolRegistry(Protocol):
    def register(self, definition: ToolDefinition) -> ToolMetadata: ...

    def update(self, metadata: ToolMetadata) -> None: ...

    def get(self, identifier: str) -> ToolMetadata | None: ...

    def list(self) -> tuple[ToolMetadata, ...]: ...

    def list_by_status(self, status: ToolStatus) -> tuple[ToolMetadata, ...]: ...

    def deregister(self, identifier: str) -> None: ...


class DiscoveryEngine(Protocol):
    def find_by_identifier(self, identifier: str) -> ToolDefinition | None: ...

    def find_by_category(self, category: ToolCategory) -> tuple[ToolDefinition, ...]: ...

    def find_by_capability(self, capability: ToolCapability) -> tuple[ToolDefinition, ...]: ...

    def find_by_workspace(self, workspace: str) -> tuple[ToolDefinition, ...]: ...

    def search(self, query: str) -> tuple[ToolDefinition, ...]: ...

    def composite_query(self, criteria: dict[str, str]) -> tuple[ToolDefinition, ...]: ...


class ValidationEngine(Protocol):
    def validate_input(
        self,
        definition: ToolDefinition,
        parameters: dict[str, str],
    ) -> ToolValidationReport: ...

    def validate_output(
        self,
        definition: ToolDefinition,
        output: str,
    ) -> ToolValidationReport: ...

    def validate_permissions(
        self,
        definition: ToolDefinition,
        agent_id: str,
        workspace: str,
    ) -> ToolValidationReport: ...

    def validate_execution_policy(
        self,
        definition: ToolDefinition,
        workspace: str,
    ) -> ToolValidationReport: ...

    def validate_all(
        self,
        definition: ToolDefinition,
        parameters: dict[str, str],
        agent_id: str,
        workspace: str,
    ) -> ToolValidationReport: ...


class ToolExecutor(Protocol):
    def can_execute(self, identifier: str) -> bool: ...

    def execute(
        self, definition: ToolDefinition, params: dict[str, str]
    ) -> ToolExecutionResult: ...


class ExecutionEngine(Protocol):
    def register_executor(self, tool_identifier: str, executor: ToolExecutor) -> None: ...

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult: ...

    def get_status(self, request_id: str) -> ExecutionStatus | None: ...

    def get_result(self, request_id: str) -> ToolExecutionResult | None: ...

    def cancel(self, request_id: str) -> None: ...

    def list_active(self) -> tuple[ToolExecutionRequest, ...]: ...


class PermissionManager(Protocol):
    def check_permission(
        self,
        tool_identifier: str,
        resource: str,
        access: str,
        scope: str,
    ) -> bool: ...

    def grant_permission(
        self,
        tool_identifier: str,
        permission: ToolPermission,
    ) -> None: ...

    def revoke_permission(
        self,
        tool_identifier: str,
        resource: str,
        scope: str,
    ) -> None: ...


class PolicyEngine(Protocol):
    def register_policy(self, scope: ToolPolicyScope, policy: ToolPolicy) -> None: ...

    def resolve(self, scope: ToolPolicyScope) -> ToolPolicy: ...

    def evaluate(self, tool_identifier: str, policy: ToolPolicy) -> tuple[str, ...]: ...


class HealthMonitor(Protocol):
    def record_execution(
        self,
        tool_identifier: str,
        duration_ms: int,
        success: bool,
    ) -> ToolHealthReport: ...

    def record_failure(
        self,
        tool_identifier: str,
        error_message: str,
    ) -> ToolHealthReport: ...

    def get_report(self, tool_identifier: str) -> ToolHealthReport | None: ...

    def list_reports(self) -> tuple[ToolHealthReport, ...]: ...

    def list_unhealthy(self) -> tuple[ToolHealthReport, ...]: ...
