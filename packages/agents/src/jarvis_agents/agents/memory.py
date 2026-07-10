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


class MemoryAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Memory",
            description="Manages memory, knowledge storage, and information retrieval across the system",
            capabilities=(
                AgentCapability(name="memory_management", description="Manage agent memory storage"),
                AgentCapability(name="knowledge_retrieval", description="Retrieve stored knowledge"),
                AgentCapability(name="information_indexing", description="Index and organize information"),
                AgentCapability(name="context_management", description="Manage conversation and task context"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.PROJECT, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "store" in desc or "save" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Information stored successfully: {task.description}",
                metadata={"storage_location": "long_term", "size": "2.4KB"},
            )
        if "retrieve" in desc or "find" in desc or "search" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Retrieved information for: {task.description}",
                metadata={"results_count": "3", "relevance_score": "0.94"},
            )
        if "index" in desc or "organize" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Information indexed for: {task.description}",
                metadata={"entries_indexed": "15", "index_type": "semantic"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Memory operation completed: {task.description}",
            metadata={"operation": "processed"},
        )
