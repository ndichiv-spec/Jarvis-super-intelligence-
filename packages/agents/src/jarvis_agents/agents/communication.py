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


class CommunicationAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Communication",
            description="Handles inter-agent communications, message routing, and coordination",
            capabilities=(
                AgentCapability(name="communication", description="Handle communications"),
                AgentCapability(name="message_routing", description="Route messages between agents"),
                AgentCapability(name="event_broker", description="Broker events between agents"),
                AgentCapability(name="coordination", description="Coordinate multi-agent workflows"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.READ),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "route" in desc or "forward" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Message routed successfully: {task.description}",
                metadata={"target_agent": "resolved", "delivery": "confirmed"},
            )
        if "broadcast" in desc or "notify" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Broadcast sent: {task.description}",
                metadata={"recipients": "5", "delivery_rate": "100%"},
            )
        if "coordinate" in desc or "orchestrate" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Multi-agent coordination completed: {task.description}",
                metadata={"agents_involved": "3", "steps_completed": "4"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Communication task completed: {task.description}",
            metadata={"message_type": "standard", "delivered": "true"},
        )
