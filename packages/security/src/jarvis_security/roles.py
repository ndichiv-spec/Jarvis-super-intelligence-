from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class PredefinedRole(Enum):
    OWNER = "owner"
    ADMINISTRATOR = "administrator"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    VIEWER = "viewer"
    AUTOMATION_MANAGER = "automation_manager"
    EXTENSION_PUBLISHER = "extension_publisher"
    ENTERPRISE_ADMINISTRATOR = "enterprise_administrator"


@dataclass(frozen=True, slots=True)
class Capability:
    namespace: str
    action: str
    resource: str

    def __post_init__(self) -> None:
        if not self.namespace.strip():
            raise ValueError("namespace cannot be empty")
        if not self.action.strip():
            raise ValueError("action cannot be empty")
        if not self.resource.strip():
            raise ValueError("resource cannot be empty")

    @property
    def key(self) -> str:
        return f"{self.namespace}:{self.action}:{self.resource}"


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    metadata: SecurityMetadata
    name: str
    description: str
    permissions: tuple[str, ...]
    capabilities: tuple[Capability, ...]
    inherited_roles: tuple[str, ...] = ()
    predefined: bool = False

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.ROLE:
            raise ValueError("metadata.object_type must be role")
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str,
        permissions: tuple[str, ...],
        capabilities: tuple[Capability, ...],
        owner_identifier: str,
        inherited_roles: tuple[str, ...] = (),
        predefined: bool = False,
    ) -> RoleDefinition:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.ROLE,
                owner_identifier=owner_identifier,
            ),
            name=name,
            description=description,
            permissions=permissions,
            capabilities=capabilities,
            inherited_roles=inherited_roles,
            predefined=predefined,
        )


def _permission(domain: str, action: str, resource: str = "*") -> str:
    return f"{domain}:{action}:{resource}"


def _cap(namespace: str, action: str, resource: str = "*") -> Capability:
    return Capability(namespace=namespace, action=action, resource=resource)


_PREDEFINED_ROLE_SPECS: tuple[
    tuple[PredefinedRole, str, tuple[str, ...], tuple[Capability, ...], tuple[str, ...]],
    ...,
] = (
    (
        PredefinedRole.OWNER,
        "Workspace owner with full control and governance authority",
        (
            _permission("memory", "read"),
            _permission("memory", "write"),
            _permission("knowledge", "read"),
            _permission("knowledge", "write"),
            _permission("agents", "execute"),
            _permission("tools", "execute"),
            _permission("automation", "manage"),
            _permission("extensions", "publish"),
            _permission("projects", "manage"),
            _permission("workspaces", "administer"),
        ),
        (_cap("governance", "administer"), _cap("security", "override")),
        (),
    ),
    (
        PredefinedRole.ADMINISTRATOR,
        "Platform administrator with operational authority",
        (
            _permission("knowledge", "read"),
            _permission("knowledge", "write"),
            _permission("agents", "execute"),
            _permission("tools", "execute"),
            _permission("automation", "manage"),
            _permission("workspaces", "administer"),
        ),
        (_cap("security", "manage"), _cap("workspace", "configure")),
        (),
    ),
    (
        PredefinedRole.DEVELOPER,
        "Developer role for project and automation work",
        (
            _permission("memory", "read"),
            _permission("knowledge", "read"),
            _permission("tools", "execute"),
            _permission("automation", "manage"),
            _permission("projects", "manage"),
        ),
        (_cap("code", "contribute"), _cap("automation", "author")),
        (),
    ),
    (
        PredefinedRole.RESEARCHER,
        "Research role focused on analysis workloads",
        (
            _permission("memory", "read"),
            _permission("knowledge", "read"),
            _permission("tools", "execute"),
        ),
        (_cap("analysis", "perform"),),
        (),
    ),
    (
        PredefinedRole.VIEWER,
        "Read-only access role",
        (_permission("knowledge", "read"), _permission("memory", "read")),
        (_cap("workspace", "view"),),
        (),
    ),
    (
        PredefinedRole.AUTOMATION_MANAGER,
        "Automation governance role",
        (_permission("automation", "manage"), _permission("tools", "execute")),
        (_cap("automation", "govern"),),
        (),
    ),
    (
        PredefinedRole.EXTENSION_PUBLISHER,
        "Extension publication role",
        (_permission("extensions", "publish"), _permission("tools", "execute")),
        (_cap("extensions", "publish"),),
        (),
    ),
    (
        PredefinedRole.ENTERPRISE_ADMINISTRATOR,
        "Enterprise-wide administrator role",
        (
            _permission("workspaces", "administer"),
            _permission("projects", "manage"),
            _permission("extensions", "publish"),
        ),
        (_cap("enterprise", "administer"), _cap("governance", "enforce")),
        (PredefinedRole.ADMINISTRATOR.value,),
    ),
)


@dataclass(slots=True)
class RoleCatalog:
    _roles: dict[str, RoleDefinition] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for role_key, description, permissions, capabilities, inherited in _PREDEFINED_ROLE_SPECS:
            self.register(
                RoleDefinition.create(
                    name=role_key.value,
                    description=description,
                    permissions=permissions,
                    capabilities=capabilities,
                    inherited_roles=inherited,
                    owner_identifier="system",
                    predefined=True,
                ),
            )

    def register(self, role: RoleDefinition) -> RoleDefinition:
        self._roles[role.name] = role
        return role

    def get(self, name: str) -> RoleDefinition | None:
        return self._roles.get(name)

    def list_roles(self) -> tuple[RoleDefinition, ...]:
        return tuple(self._roles.values())

    def resolve_permissions(self, role_names: tuple[str, ...]) -> tuple[str, ...]:
        resolved: set[str] = set()
        for role_name in role_names:
            self._collect_permissions(role_name, resolved, visited=set())
        return tuple(sorted(resolved))

    def resolve_capabilities(self, role_names: tuple[str, ...]) -> tuple[Capability, ...]:
        resolved: dict[str, Capability] = {}
        for role_name in role_names:
            self._collect_capabilities(role_name, resolved, visited=set())
        return tuple(resolved[key] for key in sorted(resolved))

    def _collect_permissions(self, role_name: str, bucket: set[str], visited: set[str]) -> None:
        if role_name in visited:
            return
        visited.add(role_name)
        role = self._roles.get(role_name)
        if role is None:
            return
        bucket.update(role.permissions)
        for inherited in role.inherited_roles:
            self._collect_permissions(inherited, bucket, visited)

    def _collect_capabilities(
        self,
        role_name: str,
        bucket: dict[str, Capability],
        visited: set[str],
    ) -> None:
        if role_name in visited:
            return
        visited.add(role_name)
        role = self._roles.get(role_name)
        if role is None:
            return
        for capability in role.capabilities:
            bucket[capability.key] = capability
        for inherited in role.inherited_roles:
            self._collect_capabilities(inherited, bucket, visited)
