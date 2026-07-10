from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_automation.models import WorkflowDefinition, WorkflowMetadata, WorkflowStatus


@dataclass(slots=True)
class InMemoryWorkflowRegistry:
    _workflows: dict[str, WorkflowMetadata] = field(default_factory=dict)

    def register(self, definition: WorkflowDefinition) -> WorkflowMetadata:
        now = datetime.now(UTC)
        meta = WorkflowMetadata(
            workflow_id=definition.workflow_id,
            definition=definition,
            status=WorkflowStatus.CREATED,
            registered_at=now,
            updated_at=now,
        )
        self._workflows[definition.workflow_id] = meta
        return meta

    def update(self, metadata: WorkflowMetadata) -> None:
        if metadata.workflow_id not in self._workflows:
            msg = f"Workflow not registered: {metadata.workflow_id}"
            raise KeyError(msg)
        now = datetime.now(UTC)
        updated = WorkflowMetadata(
            workflow_id=metadata.workflow_id,
            definition=metadata.definition,
            status=metadata.status,
            registered_at=self._workflows[metadata.workflow_id].registered_at,
            updated_at=now,
        )
        self._workflows[metadata.workflow_id] = updated

    def get(self, workflow_id: str) -> WorkflowMetadata | None:
        return self._workflows.get(workflow_id)

    def list(self) -> tuple[WorkflowMetadata, ...]:
        return tuple(self._workflows.values())

    def list_by_status(self, status: WorkflowStatus) -> tuple[WorkflowMetadata, ...]:
        return tuple(m for m in self._workflows.values() if m.status == status)

    def list_by_category(self, category: str) -> tuple[WorkflowMetadata, ...]:
        return tuple(
            m for m in self._workflows.values() if m.definition.category.value == category
        )

    def deregister(self, workflow_id: str) -> None:
        self._workflows.pop(workflow_id, None)
