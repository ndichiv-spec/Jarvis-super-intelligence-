from __future__ import annotations

from dataclasses import dataclass

from jarvis_brain.models import (
    AgentContract,
    Decision,
    DecisionAction,
    ExecutionContext,
    ExecutionPlan,
    Intent,
)


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    name: str
    responsibility: str


class RuleBasedAgentCoordinator:
    def __init__(self, *, availability: dict[str, bool] | None = None) -> None:
        self._availability = availability or {}
        self._catalog: tuple[AgentDefinition, ...] = (
            AgentDefinition(name="research", responsibility="Long-horizon research coordination"),
            AgentDefinition(name="engineering", responsibility="Engineering problem decomposition"),
            AgentDefinition(name="automation", responsibility="Automation workflow planning"),
            AgentDefinition(name="vision", responsibility="Vision workload coordination"),
            AgentDefinition(name="voice", responsibility="Voice workload coordination"),
        )

    def prepare_agents(
        self,
        intent: Intent,
        plan: ExecutionPlan,
        decision: Decision,
        context: ExecutionContext,
    ) -> tuple[AgentContract, ...]:
        _ = (plan, context)
        if decision.action != DecisionAction.DELEGATE_TO_AGENTS:
            return ()

        selected_agents: list[AgentDefinition] = []
        query = intent.normalized_query
        if "research" in query:
            selected_agents.append(self._by_name("research"))
        if any(token in query for token in ("code", "build", "refactor", "engineering")):
            selected_agents.append(self._by_name("engineering"))
        if any(token in query for token in ("automate", "workflow", "pipeline")):
            selected_agents.append(self._by_name("automation"))
        if "vision" in query:
            selected_agents.append(self._by_name("vision"))
        if "voice" in query:
            selected_agents.append(self._by_name("voice"))

        if not selected_agents:
            selected_agents.append(self._by_name("research"))

        contracts = [
            AgentContract(
                agent_name=agent.name,
                responsibility=agent.responsibility,
                available=self._availability.get(agent.name, True),
            )
            for agent in dict.fromkeys(selected_agents)
        ]
        return tuple(contracts)

    def _by_name(self, name: str) -> AgentDefinition:
        for agent in self._catalog:
            if agent.name == name:
                return agent
        raise ValueError(f"Unknown agent: {name}")
