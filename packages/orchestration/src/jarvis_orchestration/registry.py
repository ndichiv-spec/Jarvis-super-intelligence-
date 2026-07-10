from __future__ import annotations

from typing import Any

from jarvis_orchestration.models import Workflow, WorkflowPriority


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def add(self, workflow: Workflow) -> Workflow:
        self._workflows[workflow.id] = workflow
        return workflow

    def get(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def remove(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None

    def list(self, priority: WorkflowPriority | None = None, owner: str | None = None) -> list[Workflow]:
        workflows = list(self._workflows.values())
        if priority:
            workflows = [w for w in workflows if w.priority == priority]
        if owner:
            workflows = [w for w in workflows if w.owner == owner]
        return sorted(workflows, key=lambda w: w.created_at, reverse=True)

    def count(self) -> int:
        return len(self._workflows)

    def search(self, query: str) -> list[Workflow]:
        q = query.lower()
        return [w for w in self._workflows.values() if q in w.name.lower() or q in w.description.lower()]
