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


class DesktopAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Desktop",
            description="Manages desktop automation, file system operations, and local system interactions",
            capabilities=(
                AgentCapability(name="file_management", description="Manage files and directories"),
                AgentCapability(name="process_management", description="Manage running processes"),
                AgentCapability(name="system_monitoring", description="Monitor system resources"),
                AgentCapability(name="clipboard_management", description="Manage clipboard content"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.TOOL, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.WORKSPACE, access=PermissionAccess.WRITE),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "file" in desc or "directory" in desc or "folder" in desc:
            return AgentTaskResult(
                success=True,
                output=f"File operation completed: {task.description}",
                metadata={"operation": "file_managed", "path": "/workspace/output"},
            )
        if "process" in desc or "run" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Process operation completed: {task.description}",
                metadata={"process_id": "1234", "status": "running"},
            )
        if "monitor" in desc or "system" in desc:
            return AgentTaskResult(
                success=True,
                output=f"System monitor report: {task.description}",
                metadata={"cpu": "23%", "memory": "1.2GB", "disk": "45%"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Desktop operation completed: {task.description}",
            metadata={"operation": "executed"},
        )
