from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_tools.models import PermissionAccess, ToolPermission


@dataclass(slots=True)
class InMemoryPermissionManager:
    _permissions: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)

    def check_permission(
        self,
        tool_identifier: str,
        resource: str,
        access: str,
        scope: str,
    ) -> bool:
        tool_perms = self._permissions.get(tool_identifier, {})
        resource_perms = tool_perms.get(resource, {})
        granted = resource_perms.get(scope)
        if granted is None:
            granted = resource_perms.get("*")
        if granted is None:
            return False
        levels = {
            PermissionAccess.NONE.value: 0,
            PermissionAccess.READ.value: 1,
            PermissionAccess.WRITE.value: 2,
            PermissionAccess.ADMIN.value: 3,
        }
        required_level = levels.get(access, 0)
        granted_level = levels.get(granted, 0)
        return granted_level >= required_level

    def grant_permission(
        self,
        tool_identifier: str,
        permission: ToolPermission,
    ) -> None:
        if tool_identifier not in self._permissions:
            self._permissions[tool_identifier] = {}
        resource_key = permission.resource.value
        if resource_key not in self._permissions[tool_identifier]:
            self._permissions[tool_identifier][resource_key] = {}
        self._permissions[tool_identifier][resource_key][permission.scope] = permission.access.value

    def revoke_permission(
        self,
        tool_identifier: str,
        resource: str,
        scope: str,
    ) -> None:
        tool_perms = self._permissions.get(tool_identifier)
        if tool_perms is None:
            return
        resource_perms = tool_perms.get(resource)
        if resource_perms is None:
            return
        resource_perms.pop(scope, None)
        if not resource_perms:
            tool_perms.pop(resource, None)
        if not tool_perms:
            self._permissions.pop(tool_identifier, None)
