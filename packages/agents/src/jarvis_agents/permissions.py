from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.models import (
    AgentMetadata,
    AgentPermission,
    PermissionAccess,
)


@dataclass(slots=True)
class InMemoryPermissionManager:
    _grants: dict[str, list[AgentPermission]] = field(default_factory=dict)

    def check_permission(
        self,
        agent: AgentMetadata,
        resource: str,
        access: str,
        scope: str = "*",
    ) -> bool:
        for perm in agent.permissions:
            if perm.resource.value != resource and perm.resource.name.lower() != resource.lower():
                continue
            if perm.scope != "*" and perm.scope != scope:
                continue
            if self._access_level(perm.access) >= self._access_level(PermissionAccess(access)):
                return True
        granted = self._grants.get(agent.identifier, [])
        for perm in granted:
            if perm.resource.value != resource and perm.resource.name.lower() != resource.lower():
                continue
            if perm.scope != "*" and perm.scope != scope:
                continue
            if self._access_level(perm.access) >= self._access_level(PermissionAccess(access)):
                return True
        return False

    def grant_permission(self, identifier: str, permission: AgentPermission) -> None:
        if identifier not in self._grants:
            self._grants[identifier] = []
        self._grants[identifier].append(permission)

    def revoke_permission(self, identifier: str, resource: str, scope: str = "*") -> None:
        existing = self._grants.get(identifier, [])
        self._grants[identifier] = [
            p
            for p in existing
            if not (p.resource.value == resource or p.resource.name.lower() == resource.lower())
            and not (scope != "*" and p.scope == scope)
        ]

    @staticmethod
    def _access_level(access: PermissionAccess) -> int:
        levels = {
            PermissionAccess.NONE: 0,
            PermissionAccess.READ: 1,
            PermissionAccess.WRITE: 2,
            PermissionAccess.ADMIN: 3,
        }
        return levels.get(access, 0)
