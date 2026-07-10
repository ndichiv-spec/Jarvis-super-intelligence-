from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryToolInterface:
    _tools: dict[str, str] = field(default_factory=dict)
    _access: dict[str, list[str]] = field(default_factory=dict)

    def register_tool(self, tool_name: str, description: str) -> None:
        self._tools[tool_name] = description

    def grant_access(self, agent_id: str, tool_name: str) -> None:
        if agent_id not in self._access:
            self._access[agent_id] = []
        if tool_name not in self._access[agent_id]:
            self._access[agent_id].append(tool_name)

    def execute(self, agent_id: str, tool_name: str, parameters: str) -> str:
        if not self.check_access(agent_id, tool_name):
            msg = f"Agent {agent_id} does not have access to tool {tool_name}"
            raise PermissionError(msg)
        if tool_name not in self._tools:
            msg = f"Tool not found: {tool_name}"
            raise KeyError(msg)
        return f"Executed {tool_name} with parameters: {parameters}"

    def list_available(self, agent_id: str) -> tuple[str, ...]:
        allowed = self._access.get(agent_id, [])
        return tuple(t for t in self._tools if t in allowed)

    def check_access(self, agent_id: str, tool_name: str) -> bool:
        return tool_name in self._access.get(agent_id, [])
