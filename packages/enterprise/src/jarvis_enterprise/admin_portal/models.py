"""Admin portal domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class AuditEventType(StrEnum):
    organization_created = "organization_created"
    organization_updated = "organization_updated"
    workspace_created = "workspace_created"
    workspace_updated = "workspace_updated"
    user_invited = "user_invited"
    user_suspended = "user_suspended"
    policy_created = "policy_created"
    policy_updated = "policy_updated"
    integration_configured = "integration_configured"
    security_incident = "security_incident"
    configuration_changed = "configuration_changed"


@dataclass(frozen=True, slots=True)
class AuditLogEntry:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    event_type: AuditEventType = AuditEventType.organization_created
    actor_id: str = ""
    target_type: str = ""
    target_id: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PlatformConfiguration:
    key: str = ""
    value: Any = None
    category: str = "general"
    description: str = ""
    updated_by: str = ""
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class AdminDashboard:
    total_organizations: int = 0
    total_workspaces: int = 0
    total_users: int = 0
    total_incidents: int = 0
    active_policies: int = 0
    system_status: str = "healthy"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
