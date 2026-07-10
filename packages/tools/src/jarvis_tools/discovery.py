from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_tools.models import (
    ToolCapability,
    ToolCategory,
    ToolDefinition,
    ToolMetadata,
    ToolStatus,
)


@dataclass(slots=True)
class InMemoryDiscoveryEngine:
    _tools: dict[str, ToolDefinition] = field(default_factory=dict)

    def sync(self, tools: tuple[ToolMetadata, ...]) -> None:
        self._tools = {m.identifier: m.definition for m in tools}

    def _active(self) -> tuple[ToolDefinition, ...]:
        return tuple(t for t in self._tools.values() if t.status == ToolStatus.ACTIVE)

    def find_by_identifier(self, identifier: str) -> ToolDefinition | None:
        tool = self._tools.get(identifier)
        if tool is not None and tool.status == ToolStatus.ACTIVE:
            return tool
        return None

    def find_by_category(self, category: ToolCategory) -> tuple[ToolDefinition, ...]:
        return tuple(t for t in self._active() if t.category == category)

    def find_by_capability(self, capability: ToolCapability) -> tuple[ToolDefinition, ...]:
        return tuple(t for t in self._active() if capability in t.capabilities)

    def find_by_workspace(self, workspace: str) -> tuple[ToolDefinition, ...]:
        return tuple(
            t
            for t in self._active()
            if "*" in t.execution_policy.allowed_workspaces
            or workspace in t.execution_policy.allowed_workspaces
        )

    def search(self, query: str) -> tuple[ToolDefinition, ...]:
        q = query.lower()
        results: list[ToolDefinition] = []
        for t in self._active():
            if q in t.name.lower() or q in t.description.lower() or q in t.identifier.lower():
                results.append(t)
                continue
            for cap in t.capabilities:
                if q in cap.value.lower():
                    results.append(t)
                    break
        return tuple(results)

    def composite_query(self, criteria: dict[str, str]) -> tuple[ToolDefinition, ...]:
        results = list(self._active())
        for key, value in criteria.items():
            lower = value.lower()
            if key == "category":
                results = [t for t in results if t.category.value == lower]
            elif key == "capability":
                results = [t for t in results if any(c.value == lower for c in t.capabilities)]
            elif key == "workspace":
                results = [
                    t
                    for t in results
                    if "*" in t.execution_policy.allowed_workspaces
                    or lower in t.execution_policy.allowed_workspaces
                ]
            elif key == "owner":
                results = [t for t in results if t.owner == value]
            elif key == "version":
                results = [t for t in results if t.version == value]
            elif key == "status":
                results = [t for t in results if t.status.value == lower]
        return tuple(results)
