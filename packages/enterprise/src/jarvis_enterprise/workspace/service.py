"""Workspace administration service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.workspace.models import (
    Project,
    ResourceAllocation,
    Workspace,
    WorkspaceMembership,
    WorkspaceStatus,
    WorkspaceVisibility,
)
from jarvis_enterprise.workspace.repository import WorkspaceRepository


class WorkspaceAdministrationService:
    def __init__(self, repository: WorkspaceRepository) -> None:
        self._repository = repository

    def create_workspace(
        self,
        org_id: UUID,
        name: str,
        owner_id: str,
        display_name: str = "",
        description: str = "",
        visibility: WorkspaceVisibility = WorkspaceVisibility.private,
    ) -> Workspace:
        ws = Workspace(
            org_id=org_id, name=name, display_name=display_name or name,
            description=description, owner_id=owner_id, visibility=visibility,
        )
        self._repository.save(ws)
        return ws

    def get_workspace(self, workspace_id: UUID) -> Workspace | None:
        return self._repository.get(workspace_id)

    def suspend_workspace(self, workspace_id: UUID) -> Workspace | None:
        ws = self._repository.get(workspace_id)
        if ws is None:
            return None
        updated = Workspace(
            id=ws.id, org_id=ws.org_id, name=ws.name, display_name=ws.display_name,
            description=ws.description, status=WorkspaceStatus.suspended, visibility=ws.visibility,
            owner_id=ws.owner_id, tags=ws.tags, metadata=ws.metadata,
            created_at=ws.created_at,
        )
        self._repository.save(updated)
        return updated

    def list_workspaces(self, org_id: UUID) -> list[Workspace]:
        return self._repository.list_by_org(org_id)

    def add_member(self, workspace_id: UUID, user_id: str, role: str = "viewer") -> WorkspaceMembership | None:
        ws = self._repository.get(workspace_id)
        if ws is None:
            return None
        membership = WorkspaceMembership(workspace_id=workspace_id, user_id=user_id, role=role)
        self._repository.add_member(workspace_id, membership)
        return membership

    def remove_member(self, workspace_id: UUID, user_id: str) -> bool:
        ws = self._repository.get(workspace_id)
        if ws is None:
            return False
        self._repository.remove_member(workspace_id, user_id)
        return True

    def get_members(self, workspace_id: UUID) -> list[WorkspaceMembership]:
        return self._repository.get_members(workspace_id)

    def create_project(self, workspace_id: UUID, name: str, owner_id: str, description: str = "") -> Project | None:
        ws = self._repository.get(workspace_id)
        if ws is None:
            return None
        project = Project(workspace_id=workspace_id, name=name, description=description, owner_id=owner_id)
        self._repository.save_project(project)
        return project

    def list_projects(self, workspace_id: UUID) -> list[Project]:
        return self._repository.list_projects(workspace_id)

    def set_resource_allocation(
        self, workspace_id: UUID, resource_type: str, limit: int,
    ) -> ResourceAllocation | None:
        ws = self._repository.get(workspace_id)
        if ws is None:
            return None
        allocation = ResourceAllocation(workspace_id=workspace_id, resource_type=resource_type, limit=limit)
        self._repository.set_allocation(allocation)
        return allocation

    def get_resource_allocation(self, workspace_id: UUID, resource_type: str) -> ResourceAllocation | None:
        return self._repository.get_allocation(workspace_id, resource_type)
