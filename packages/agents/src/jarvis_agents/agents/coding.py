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


class CodingAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Coding",
            description="Writes code, reviews implementations, and solves engineering problems",
            capabilities=(
                AgentCapability(name="programming", description="Write and review code"),
                AgentCapability(name="architecture", description="Design software architecture"),
                AgentCapability(name="code_review", description="Review code for quality"),
                AgentCapability(name="debugging", description="Debug issues in code"),
                AgentCapability(name="optimization", description="Optimize performance"),
                AgentCapability(name="testing", description="Write and execute tests"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.TOOL, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "review" in desc or "code review" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Code review completed for: {task.description}",
                metadata={"issues_found": "2", "quality_score": "0.85"},
            )
        if "debug" in desc or "fix" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Debugged and fixed issue: {task.description}",
                metadata={"root_cause": "logic error", "fix": "applied"},
            )
        if "test" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Tests written for: {task.description}",
                metadata={"test_count": "5", "coverage": "87%"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Generated implementation for: {task.description}",
            metadata={"language": "python", "lines_of_code": "42"},
        )
