from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_extensions.models import PermissionRequest, PermissionScope


@dataclass(slots=True)
class InMemoryPermissionManager:
    _grants: dict[str, dict[PermissionScope, PermissionRequest]] = field(default_factory=dict)

    def grant(self, extension_id: str, permission: PermissionRequest) -> None:
        if extension_id not in self._grants:
            self._grants[extension_id] = {}
        self._grants[extension_id][permission.permission_scope] = permission

    def revoke(self, extension_id: str, scope: PermissionScope) -> None:
        grants = self._grants.get(extension_id)
        if grants is not None:
            grants.pop(scope, None)

    def check(self, extension_id: str, scope: PermissionScope) -> bool:
        grants = self._grants.get(extension_id)
        if grants is None:
            return False
        return scope in grants

    def list_permissions(self, extension_id: str) -> tuple[PermissionRequest, ...]:
        grants = self._grants.get(extension_id)
        if grants is None:
            return ()
        return tuple(grants.values())

    def revoke_all(self, extension_id: str) -> None:
        self._grants.pop(extension_id, None)
