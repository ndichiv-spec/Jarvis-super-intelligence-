from __future__ import annotations

from dataclasses import dataclass

from jarvis_brain.models import (
    Capability,
    Decision,
    DecisionAction,
    ExecutionContext,
    ExecutionPlan,
    Intent,
    ToolContract,
)


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    purpose: str
    required_permissions: tuple[str, ...]


class RuleBasedToolCoordinator:
    def __init__(
        self,
        *,
        permissions: dict[str, bool] | None = None,
        availability: dict[str, bool] | None = None,
    ) -> None:
        self._permissions = permissions or {}
        self._availability = availability or {}
        self._catalog: dict[Capability, tuple[ToolDefinition, ...]] = {
            Capability.RESEARCH: (
                ToolDefinition(
                    name="research_index",
                    purpose="Collect and index research references.",
                    required_permissions=("research:read",),
                ),
            ),
            Capability.KNOWLEDGE_QUERY: (
                ToolDefinition(
                    name="knowledge_query",
                    purpose="Query approved knowledge sources.",
                    required_permissions=("knowledge:read",),
                ),
            ),
            Capability.TOOL_COORDINATION: (
                ToolDefinition(
                    name="workspace_automation",
                    purpose="Coordinate workspace-level actions.",
                    required_permissions=("workspace:execute",),
                ),
                ToolDefinition(
                    name="system_executor",
                    purpose="Coordinate system-safe command contracts.",
                    required_permissions=("system:execute",),
                ),
            ),
        }

    def prepare_tools(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        decision: Decision,
        context: ExecutionContext,
    ) -> tuple[ToolContract, ...]:
        _ = (plan, context)
        if decision.action not in (DecisionAction.INVOKE_TOOLS, DecisionAction.RESEARCH):
            return ()

        selected_capabilities = set(intent.required_capabilities)
        if decision.action == DecisionAction.INVOKE_TOOLS:
            selected_capabilities.add(Capability.TOOL_COORDINATION)
        if decision.action == DecisionAction.RESEARCH:
            selected_capabilities.add(Capability.RESEARCH)

        contracts: list[ToolContract] = []
        for capability in selected_capabilities:
            for definition in self._catalog.get(capability, ()):
                allowed = all(
                    self._permissions.get(permission, True)
                    for permission in definition.required_permissions
                )
                available = self._availability.get(definition.name, True)
                contracts.append(
                    ToolContract(
                        tool_name=definition.name,
                        purpose=definition.purpose,
                        required_permissions=definition.required_permissions,
                        available=available,
                        allowed=allowed,
                    )
                )
        return tuple(contracts)
