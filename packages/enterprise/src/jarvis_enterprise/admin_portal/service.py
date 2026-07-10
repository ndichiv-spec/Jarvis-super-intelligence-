"""Administration portal service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.admin_portal.models import (
    AdminDashboard,
    AuditEventType,
    AuditLogEntry,
    PlatformConfiguration,
)


class AdministrationPortalService:
    def __init__(self) -> None:
        self._audit_log: list[AuditLogEntry] = []
        self._config: dict[str, PlatformConfiguration] = {}

    def log_event(
        self, org_id: UUID, event_type: AuditEventType,
        actor_id: str, target_type: str = "", target_id: str = "",
        details: dict | None = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            org_id=org_id, event_type=event_type, actor_id=actor_id,
            target_type=target_type, target_id=target_id, details=details or {},
        )
        self._audit_log.append(entry)
        return entry

    def get_audit_log(self, org_id: UUID, limit: int = 100) -> list[AuditLogEntry]:
        return [e for e in self._audit_log if e.org_id == org_id][-limit:]

    def set_configuration(self, key: str, value: Any, category: str = "general", updated_by: str = "", description: str = "") -> PlatformConfiguration:
        config = PlatformConfiguration(
            key=key, value=value, category=category,
            description=description, updated_by=updated_by,
        )
        self._config[key] = config
        return config

    def get_configuration(self, key: str) -> PlatformConfiguration | None:
        return self._config.get(key)

    def list_configurations(self, category: str | None = None) -> list[PlatformConfiguration]:
        if category:
            return [c for c in self._config.values() if c.category == category]
        return list(self._config.values())

    def get_dashboard(self, org_count: int = 0, ws_count: int = 0, user_count: int = 0) -> AdminDashboard:
        return AdminDashboard(
            total_organizations=org_count,
            total_workspaces=ws_count,
            total_users=user_count,
            total_incidents=sum(1 for e in self._audit_log if e.event_type == AuditEventType.security_incident),
            active_policies=sum(1 for e in self._audit_log if e.event_type == AuditEventType.policy_created),
        )
