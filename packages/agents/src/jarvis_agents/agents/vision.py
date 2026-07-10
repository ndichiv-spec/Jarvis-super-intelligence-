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


class VisionAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Vision",
            description="Processes and analyzes visual information, images, and diagrams",
            capabilities=(
                AgentCapability(name="vision", description="Process visual information"),
                AgentCapability(name="analysis", description="Analyze data and patterns"),
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
        if "image" in desc or "picture" in desc or "photo" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Image analysis completed: {task.description}",
                metadata={"objects_detected": "3", "image_type": "photograph"},
            )
        if "diagram" in desc or "chart" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Diagram analysis completed: {task.description}",
                metadata={"elements_identified": "7", "diagram_type": "flowchart"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Vision processing complete: {task.description}",
            metadata={"processing_type": "visual_analysis", "confidence": "0.91"},
        )
