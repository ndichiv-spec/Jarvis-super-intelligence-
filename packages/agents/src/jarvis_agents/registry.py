from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.models import AgentMetadata, AgentStatus


@dataclass(slots=True)
class InMemoryAgentRegistry:
    _agents: dict[str, AgentMetadata] = field(default_factory=dict)

    def register(self, agent: AgentMetadata) -> None:
        self._agents[agent.identifier] = agent

    def update(self, agent: AgentMetadata) -> None:
        if agent.identifier not in self._agents:
            msg = f"Agent is not registered: {agent.identifier}"
            raise KeyError(msg)
        self._agents[agent.identifier] = agent

    def get(self, identifier: str) -> AgentMetadata | None:
        return self._agents.get(identifier)

    def list(self) -> tuple[AgentMetadata, ...]:
        return tuple(self._agents.values())

    def list_by_status(self, status: AgentStatus) -> tuple[AgentMetadata, ...]:
        return tuple(a for a in self._agents.values() if a.status == status)

    def list_by_capability(self, capability_name: str) -> tuple[AgentMetadata, ...]:
        return tuple(
            a
            for a in self._agents.values()
            if any(c.name == capability_name for c in a.capabilities)
        )

    def deregister(self, identifier: str) -> None:
        self._agents.pop(identifier, None)
