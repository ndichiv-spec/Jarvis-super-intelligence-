from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.models import AgentCapability, AgentMetadata, AgentStatus
from jarvis_agents.registry import InMemoryAgentRegistry


@dataclass(slots=True)
class CapabilityMatch:
    agent: AgentMetadata
    matched_capabilities: tuple[AgentCapability, ...]
    score: float


@dataclass(slots=True)
class InMemoryAgentDiscovery:
    _registry: InMemoryAgentRegistry
    _capability_index: dict[str, list[str]] = field(default_factory=dict)

    def build_index(self) -> None:
        self._capability_index.clear()
        for agent in self._registry.list():
            for cap in agent.capabilities:
                if cap.name not in self._capability_index:
                    self._capability_index[cap.name] = []
                self._capability_index[cap.name].append(agent.identifier)

    def find_by_capability(
        self,
        capability_name: str,
        *,
        min_status: AgentStatus = AgentStatus.READY,
    ) -> tuple[AgentMetadata, ...]:
        agent_ids = self._capability_index.get(capability_name, [])
        results: list[AgentMetadata] = []
        for aid in agent_ids:
            agent = self._registry.get(aid)
            if agent is None:
                continue
            if agent.status.value <= min_status.value:
                results.append(agent)
        return tuple(results)

    def find_by_multiple_capabilities(
        self,
        capability_names: set[str],
        *,
        require_all: bool = True,
        min_status: AgentStatus = AgentStatus.READY,
    ) -> tuple[CapabilityMatch, ...]:
        matches: list[CapabilityMatch] = []
        for agent in self._registry.list():
            if agent.status.value > min_status.value:
                continue
            matched = tuple(c for c in agent.capabilities if c.name in capability_names)
            if require_all and len(matched) < len(capability_names):
                continue
            if not matched:
                continue
            score = len(matched) / len(capability_names) if capability_names else 0.0
            matches.append(CapabilityMatch(agent=agent, matched_capabilities=matched, score=score))
        matches.sort(key=lambda m: m.score, reverse=True)
        return tuple(matches)

    def find_by_workspace(
        self,
        workspace: str,
        *,
        min_status: AgentStatus = AgentStatus.READY,
    ) -> tuple[AgentMetadata, ...]:
        return tuple(
            a for a in self._registry.list()
            if a.workspace == workspace and a.status.value <= min_status.value
        )

    def find_nearest_capability(
        self,
        capability_name: str,
        *,
        min_status: AgentStatus = AgentStatus.READY,
    ) -> AgentMetadata | None:
        agents = self.find_by_capability(capability_name, min_status=min_status)
        return agents[0] if agents else None

    def count_by_capability(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for agent in self._registry.list():
            for cap in agent.capabilities:
                counts[cap.name] = counts.get(cap.name, 0) + 1
        return counts

    def list_all_capabilities(self) -> tuple[AgentCapability, ...]:
        seen: dict[str, AgentCapability] = {}
        for agent in self._registry.list():
            for cap in agent.capabilities:
                if cap.name not in seen:
                    seen[cap.name] = cap
        return tuple(seen.values())
