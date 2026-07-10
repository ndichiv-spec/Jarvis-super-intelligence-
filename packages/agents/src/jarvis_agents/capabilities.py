from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.models import AgentCapability, AgentMetadata


@dataclass(slots=True)
class InMemoryCapabilityManager:
    _capabilities: dict[str, AgentCapability] = field(default_factory=dict)

    def register_capability(self, capability: AgentCapability) -> None:
        self._capabilities[capability.name] = capability

    def get_capability(self, name: str) -> AgentCapability | None:
        return self._capabilities.get(name)

    def list_capabilities(self) -> tuple[AgentCapability, ...]:
        return tuple(self._capabilities.values())

    def has_capability(self, agent: AgentMetadata, capability_name: str) -> bool:
        return any(c.name == capability_name for c in agent.capabilities)

    def find_agents_with_capability(
        self,
        agents: tuple[AgentMetadata, ...],
        capability_name: str,
    ) -> tuple[AgentMetadata, ...]:
        return tuple(a for a in agents if self.has_capability(a, capability_name))
