from __future__ import annotations

from jarvis_agents.agents.base import BaseAgent
from jarvis_agents.models import (
    AgentCapability,
    AgentPermission,
    AgentPermissionResource,
    AgentTask,
    AgentTaskResult,
    PermissionAccess,
)


class PlannerAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Planner",
            description="Creates plans, decomposes work, and tracks progress",
            capabilities=(
                AgentCapability(name="planning", description="Create and manage plans"),
                AgentCapability(name="analysis", description="Analyze data and patterns"),
                AgentCapability(name="reasoning", description="Perform logical reasoning"),
                AgentCapability(name="reporting", description="Generate reports"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "plan" in desc or "decompose" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Created plan with decomposed subtasks for: {task.description}",
                metadata={"plan_status": "ready"},
            )
        if "progress" in desc or "track" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Progress tracked for: {task.description}",
                metadata={"progress": "50%"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Planning analysis complete for: {task.description}",
            metadata={"analysis": "complete"},
        )
