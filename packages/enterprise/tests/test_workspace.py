"""Tests for Workspace Administration."""

from uuid import uuid4

from jarvis_enterprise.workspace.models import (
    Project,
    ResourceAllocation,
    Workspace,
    WorkspaceMembership,
    WorkspaceStatus,
    WorkspaceVisibility,
)
from jarvis_enterprise.workspace.repository import WorkspaceRepository
from jarvis_enterprise.workspace.service import WorkspaceAdministrationService


class InMemoryWorkspaceRepository:
    def __init__(self):
        self._workspaces: dict = {}
        self._members: dict = {}
        self._projects: dict = {}
        self._allocations: dict = {}

    def save(self, ws: Workspace) -> None:
        self._workspaces[ws.id] = ws

    def get(self, ws_id) -> Workspace | None:
        return self._workspaces.get(ws_id)

    def delete(self, ws_id) -> None:
        self._workspaces.pop(ws_id, None)

    def list_by_org(self, org_id) -> list[Workspace]:
        return [w for w in self._workspaces.values() if w.org_id == org_id]

    def add_member(self, ws_id, membership) -> None:
        self._members.setdefault(ws_id, []).append(membership)

    def remove_member(self, ws_id, user_id) -> None:
        self._members[ws_id] = [m for m in self._members.get(ws_id, []) if m.user_id != user_id]

    def get_members(self, ws_id) -> list[WorkspaceMembership]:
        return list(self._members.get(ws_id, []))

    def save_project(self, project) -> None:
        self._projects[project.id] = project

    def get_project(self, project_id) -> Project | None:
        return self._projects.get(project_id)

    def list_projects(self, ws_id) -> list[Project]:
        return [p for p in self._projects.values() if p.workspace_id == ws_id]

    def set_allocation(self, allocation) -> None:
        key = (allocation.workspace_id, allocation.resource_type)
        self._allocations[key] = allocation

    def get_allocation(self, ws_id, resource_type) -> ResourceAllocation | None:
        return self._allocations.get((ws_id, resource_type))


class TestWorkspaceService:
    def setup_method(self):
        self.repo = WorkspaceAdministrationService(InMemoryWorkspaceRepository())

    def test_create_and_get(self):
        org_id = uuid4()
        ws = self.repo.create_workspace(org_id, "dev-workspace", "owner1")
        assert ws.name == "dev-workspace"
        fetched = self.repo.get_workspace(ws.id)
        assert fetched is not None

    def test_suspend(self):
        ws = self.repo.create_workspace(uuid4(), "test", "owner1")
        suspended = self.repo.suspend_workspace(ws.id)
        assert suspended is not None
        assert suspended.status == WorkspaceStatus.suspended

    def test_list_by_org(self):
        org_id = uuid4()
        self.repo.create_workspace(org_id, "ws1", "owner1")
        self.repo.create_workspace(org_id, "ws2", "owner1")
        assert len(self.repo.list_workspaces(org_id)) == 2

    def test_add_remove_member(self):
        ws = self.repo.create_workspace(uuid4(), "test", "owner1")
        member = self.repo.add_member(ws.id, "user1", "editor")
        assert member is not None
        assert len(self.repo.get_members(ws.id)) == 1
        self.repo.remove_member(ws.id, "user1")
        assert len(self.repo.get_members(ws.id)) == 0

    def test_add_member_nonexistent(self):
        assert self.repo.add_member(uuid4(), "user1") is None

    def test_create_project(self):
        ws = self.repo.create_workspace(uuid4(), "test", "owner1")
        project = self.repo.create_project(ws.id, "my-project", "owner1")
        assert project is not None
        assert project.name == "my-project"

    def test_list_projects(self):
        ws = self.repo.create_workspace(uuid4(), "test", "owner1")
        self.repo.create_project(ws.id, "p1", "owner1")
        self.repo.create_project(ws.id, "p2", "owner1")
        assert len(self.repo.list_projects(ws.id)) == 2

    def test_set_resource_allocation(self):
        ws = self.repo.create_workspace(uuid4(), "test", "owner1")
        alloc = self.repo.set_resource_allocation(ws.id, "compute", 100)
        assert alloc is not None
        assert alloc.limit == 100
