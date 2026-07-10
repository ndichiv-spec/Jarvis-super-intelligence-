from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from jarvis_agents.kernel import AgentKernel
from jarvis_agents.models import AgentMetadata

from jarvis_planning.decomposer import Task
from jarvis_planning.estimator import Complexity


class AssignmentStrategy(Enum):
    CAPABILITY_MATCH = "capability_match"
    WORKLOAD_BALANCE = "workload_balance"
    CONFIDENCE_SCORE = "confidence_score"
    ROUND_ROBIN = "round_robin"


TASK_TYPE_TO_CAPABILITY: dict[str, str] = {
    "requirements": "research",
    "architecture": "architecture",
    "design": "design",
    "backend": "programming",
    "frontend": "programming",
    "mobile": "programming",
    "api": "programming",
    "database": "architecture",
    "testing": "testing",
    "deployment": "automation",
    "documentation": "documentation",
    "research": "research",
    "analysis": "analysis",
    "monitoring": "monitoring",
    "automation": "automation",
    "security": "programming",
    "integration": "automation",
    "planning": "planning",
    "reporting": "reporting",
    "communication": "communication",
}


@dataclass
class AgentAssignment:
    task_id: str
    agent_id: str
    agent_name: str
    confidence: float
    strategy: AssignmentStrategy
    capability_matched: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "confidence": self.confidence,
            "strategy": self.strategy.value,
            "capability_matched": self.capability_matched,
        }


class AgentAssigner:
    def __init__(
        self,
        agent_kernel: AgentKernel,
        strategy: AssignmentStrategy = AssignmentStrategy.CAPABILITY_MATCH,
    ) -> None:
        self._kernel = agent_kernel
        self._strategy = strategy

    @property
    def kernel(self) -> AgentKernel:
        return self._kernel

    @property
    def strategy(self) -> AssignmentStrategy:
        return self._strategy

    def assign_task(self, task: Task, available_agents: tuple[AgentMetadata, ...] | None = None) -> AgentAssignment:
        if available_agents is None:
            available_agents = self._kernel.list_ready_agents()
        capability = self._resolve_capability(task)
        if self._strategy == AssignmentStrategy.CAPABILITY_MATCH:
            return self._assign_by_capability(task, capability, available_agents)
        if self._strategy == AssignmentStrategy.WORKLOAD_BALANCE:
            return self._assign_by_workload(task, capability, available_agents)
        if self._strategy == AssignmentStrategy.CONFIDENCE_SCORE:
            return self._assign_by_confidence(task, capability, available_agents)
        return self._assign_round_robin(task, available_agents)

    def assign_tasks(
        self, tasks: list[Task], available_agents: tuple[AgentMetadata, ...] | None = None
    ) -> list[AgentAssignment]:
        if available_agents is None:
            available_agents = self._kernel.list_ready_agents()
        assignments: list[AgentAssignment] = []
        for task in tasks:
            assignment = self.assign_task(task, available_agents)
            task.assigned_agent = assignment.agent_id
            assignments.append(assignment)
        return assignments

    def _resolve_capability(self, task: Task) -> str:
        for keyword, capability in TASK_TYPE_TO_CAPABILITY.items():
            if keyword in task.title.lower() or keyword in task.description.lower():
                return capability
        return "planning"

    def _assign_by_capability(
        self, task: Task, capability: str, agents: tuple[AgentMetadata, ...]
    ) -> AgentAssignment:
        if not agents:
            return AgentAssignment(task_id=task.id, agent_id="", agent_name="unassigned", confidence=0.0, strategy=AssignmentStrategy.CAPABILITY_MATCH)
        candidates: list[AgentMetadata] = []
        for agent in agents:
            for cap in agent.capabilities:
                if cap.name == capability:
                    candidates.append(agent)
                    break
        if not candidates:
            candidates = list(agents)
        selected = candidates[0]
        return AgentAssignment(
            task_id=task.id,
            agent_id=selected.identifier,
            agent_name=selected.name,
            confidence=self._score_confidence(selected, capability),
            strategy=AssignmentStrategy.CAPABILITY_MATCH,
            capability_matched=capability,
        )

    def _assign_by_workload(
        self, task: Task, capability: str, agents: tuple[AgentMetadata, ...]
    ) -> AgentAssignment:
        if not agents:
            return AgentAssignment(task_id=task.id, agent_id="", agent_name="unassigned", confidence=0.0, strategy=AssignmentStrategy.WORKLOAD_BALANCE)
        candidates: list[AgentMetadata] = []
        for agent in agents:
            for cap in agent.capabilities:
                if cap.name == capability:
                    candidates.append(agent)
                    break
        if not candidates:
            candidates = list(agents)
        selected = min(candidates, key=lambda a: len(self._kernel.list_tasks_by_agent(a.identifier)))
        return AgentAssignment(
            task_id=task.id,
            agent_id=selected.identifier,
            agent_name=selected.name,
            confidence=self._score_confidence(selected, capability),
            strategy=AssignmentStrategy.WORKLOAD_BALANCE,
            capability_matched=capability,
        )

    def _assign_by_confidence(
        self, task: Task, capability: str, agents: tuple[AgentMetadata, ...]
    ) -> AgentAssignment:
        if not agents:
            return AgentAssignment(task_id=task.id, agent_id="", agent_name="unassigned", confidence=0.0, strategy=AssignmentStrategy.CONFIDENCE_SCORE)
        candidates: list[AgentMetadata] = []
        for agent in agents:
            for cap in agent.capabilities:
                if cap.name == capability:
                    candidates.append(agent)
                    break
        if not candidates:
            candidates = list(agents)
        selected = max(candidates, key=lambda a: self._score_confidence(a, capability))
        return AgentAssignment(
            task_id=task.id,
            agent_id=selected.identifier,
            agent_name=selected.name,
            confidence=self._score_confidence(selected, capability),
            strategy=AssignmentStrategy.CONFIDENCE_SCORE,
            capability_matched=capability,
        )

    def _assign_round_robin(self, task: Task, agents: tuple[AgentMetadata, ...]) -> AgentAssignment:
        if not agents:
            return AgentAssignment(task_id=task.id, agent_id="", agent_name="unassigned", confidence=0.0, strategy=AssignmentStrategy.ROUND_ROBIN)
        idx = hash(task.id) % max(len(agents), 1)
        selected = agents[idx]
        return AgentAssignment(
            task_id=task.id,
            agent_id=selected.identifier,
            agent_name=selected.name,
            confidence=0.5,
            strategy=AssignmentStrategy.ROUND_ROBIN,
            capability_matched="general",
        )

    def _score_confidence(self, agent: AgentMetadata, capability: str) -> float:
        score = 0.5
        for cap in agent.capabilities:
            if cap.name == capability:
                score += 0.3
                if len(agent.capabilities) <= 3:
                    score += 0.2
                break
        return min(score, 1.0)
