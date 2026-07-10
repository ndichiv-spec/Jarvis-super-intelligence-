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


class ResearchAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Research",
            description="Conducts research, gathers information, and synthesizes findings",
            capabilities=(
                AgentCapability(name="research", description="Conduct research and gather information"),
                AgentCapability(name="analysis", description="Analyze data and patterns"),
                AgentCapability(name="summarization", description="Summarize information"),
                AgentCapability(name="reasoning", description="Perform logical reasoning"),
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
        if "research" in desc or "investigate" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Research findings for: {task.description}",
                metadata={"sources_consulted": "5", "findings": "synthesized"},
            )
        if "summarize" in desc or "summary" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Summary produced for: {task.description}",
                metadata={"original_length": "2000", "summary_length": "250"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Analysis complete for: {task.description}",
            metadata={"analysis_type": "qualitative", "confidence": "0.92"},
        )
