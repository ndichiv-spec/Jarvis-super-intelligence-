from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class PermissionDomain(Enum):
    MEMORY = auto()
    KNOWLEDGE = auto()
    AGENTS = auto()
    TOOLS = auto()
    AUTOMATION = auto()
    EXTENSIONS = auto()
    PROJECTS = auto()
    WORKSPACES = auto()
    INFRASTRUCTURE = auto()


@dataclass(frozen=True, slots=True)
class Permission:
    metadata: SecurityMetadata
    domain: PermissionDomain
    action: str
    resource: str
    description: str

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.PERMISSION:
            raise ValueError("metadata.object_type must be permission")
        if not self.action.strip():
            raise ValueError("action cannot be empty")
        if not self.resource.strip():
            raise ValueError("resource cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")

    @property
    def key(self) -> str:
        return f"{self.domain.name.lower()}:{self.action}:{self.resource}"

    @classmethod
    def create(
        cls,
        *,
        domain: PermissionDomain,
        action: str,
        resource: str,
        description: str,
        owner_identifier: str,
    ) -> Permission:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.PERMISSION,
                owner_identifier=owner_identifier,
            ),
            domain=domain,
            action=action,
            resource=resource,
            description=description,
        )


_DEFAULT_PERMISSION_SPECS: tuple[tuple[PermissionDomain, str, str, str], ...] = (
    (PermissionDomain.MEMORY, "read", "*", "Read memory content"),
    (PermissionDomain.MEMORY, "write", "*", "Write memory content"),
    (PermissionDomain.KNOWLEDGE, "read", "*", "Read knowledge artifacts"),
    (PermissionDomain.KNOWLEDGE, "write", "*", "Write knowledge artifacts"),
    (PermissionDomain.AGENTS, "execute", "*", "Execute agent operations"),
    (PermissionDomain.TOOLS, "execute", "*", "Execute tool operations"),
    (PermissionDomain.AUTOMATION, "manage", "*", "Manage automation workflows"),
    (PermissionDomain.EXTENSIONS, "publish", "*", "Publish and manage extensions"),
    (PermissionDomain.PROJECTS, "manage", "*", "Manage project resources"),
    (PermissionDomain.WORKSPACES, "administer", "*", "Administer workspace settings"),
)


@dataclass(slots=True)
class PermissionCatalog:
    _permissions: dict[str, Permission] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for domain, action, resource, description in _DEFAULT_PERMISSION_SPECS:
            permission = Permission.create(
                domain=domain,
                action=action,
                resource=resource,
                description=description,
                owner_identifier="system",
            )
            self.register(permission)

    def register(self, permission: Permission) -> Permission:
        self._permissions[permission.key] = permission
        return permission

    def get(self, key: str) -> Permission | None:
        return self._permissions.get(key)

    def list_permissions(self) -> tuple[Permission, ...]:
        return tuple(self._permissions.values())
