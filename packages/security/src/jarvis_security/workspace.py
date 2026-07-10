from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


@dataclass(frozen=True, slots=True)
class WorkspaceBoundary:
    metadata: SecurityMetadata
    workspace_identifier: str
    organization_identifier: str
    isolation_key: str

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.WORKSPACE:
            raise ValueError("metadata.object_type must be workspace")
        if not self.workspace_identifier.strip():
            raise ValueError("workspace_identifier cannot be empty")
        if not self.organization_identifier.strip():
            raise ValueError("organization_identifier cannot be empty")
        if not self.isolation_key.strip():
            raise ValueError("isolation_key cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        workspace_identifier: str,
        organization_identifier: str,
        owner_identifier: str,
        isolation_key: str,
    ) -> WorkspaceBoundary:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.WORKSPACE,
                owner_identifier=owner_identifier,
                identifier=workspace_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            workspace_identifier=workspace_identifier,
            organization_identifier=organization_identifier,
            isolation_key=isolation_key,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceMembership:
    metadata: SecurityMetadata
    identity_identifier: str
    workspace_identifier: str
    organization_identifier: str
    role_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identity_identifier.strip():
            raise ValueError("identity_identifier cannot be empty")
        if not self.workspace_identifier.strip():
            raise ValueError("workspace_identifier cannot be empty")
        if not self.organization_identifier.strip():
            raise ValueError("organization_identifier cannot be empty")


class WorkspaceIsolationContract(Protocol):
    def can_access_identity(
        self,
        *,
        identity_identifier: str,
        workspace_identifier: str,
        organization_identifier: str | None,
    ) -> bool:
        ...

    def assert_isolated(self, source_workspace: str, target_workspace: str) -> bool:
        ...


@dataclass(slots=True)
class WorkspaceIsolationManager(WorkspaceIsolationContract):
    _boundaries: dict[str, WorkspaceBoundary] = field(default_factory=dict)
    _memberships_by_identity: dict[str, list[WorkspaceMembership]] = field(default_factory=dict)

    def register_boundary(self, boundary: WorkspaceBoundary) -> WorkspaceBoundary:
        self._boundaries[boundary.workspace_identifier] = boundary
        return boundary

    def get_boundary(self, workspace_identifier: str) -> WorkspaceBoundary | None:
        return self._boundaries.get(workspace_identifier)

    def add_membership(
        self,
        *,
        identity_identifier: str,
        workspace_identifier: str,
        organization_identifier: str,
        role_names: tuple[str, ...],
        owner_identifier: str,
    ) -> WorkspaceMembership:
        if workspace_identifier not in self._boundaries:
            raise KeyError(f"Unknown workspace boundary: {workspace_identifier}")
        membership = WorkspaceMembership(
            metadata=new_metadata(
                object_type=SecurityObjectType.WORKSPACE,
                owner_identifier=owner_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            identity_identifier=identity_identifier,
            workspace_identifier=workspace_identifier,
            organization_identifier=organization_identifier,
            role_names=role_names,
        )
        self._memberships_by_identity.setdefault(identity_identifier, []).append(membership)
        return membership

    def list_memberships(self, identity_identifier: str) -> tuple[WorkspaceMembership, ...]:
        return tuple(self._memberships_by_identity.get(identity_identifier, []))

    def can_access_identity(
        self,
        *,
        identity_identifier: str,
        workspace_identifier: str,
        organization_identifier: str | None,
    ) -> bool:
        boundary = self._boundaries.get(workspace_identifier)
        if boundary is None:
            return False
        memberships = self._memberships_by_identity.get(identity_identifier, [])
        for membership in memberships:
            if membership.workspace_identifier != workspace_identifier:
                continue
            if organization_identifier is None:
                return True
            if membership.organization_identifier == organization_identifier:
                return True
        return False

    def can_access_context(
        self,
        *,
        workspace_memberships: tuple[str, ...],
        organization_memberships: tuple[str, ...],
        workspace_identifier: str,
        organization_identifier: str | None,
    ) -> bool:
        if workspace_identifier not in workspace_memberships:
            return False
        boundary = self._boundaries.get(workspace_identifier)
        if boundary is None:
            return False
        if organization_identifier is None:
            return True
        return (
            organization_identifier in organization_memberships
            and organization_identifier == boundary.organization_identifier
        )

    def assert_isolated(self, source_workspace: str, target_workspace: str) -> bool:
        return source_workspace == target_workspace
