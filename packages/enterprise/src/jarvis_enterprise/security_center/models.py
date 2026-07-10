"""Security center domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class IncidentSeverity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IncidentStatus(StrEnum):
    open = "open"
    investigating = "investigating"
    contained = "contained"
    resolved = "resolved"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    enabled: bool = True
    rules: tuple[dict[str, Any], ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class SecurityDashboard:
    org_id: UUID = field(default_factory=uuid4)
    total_incidents: int = 0
    open_incidents: int = 0
    critical_incidents: int = 0
    resolved_incidents: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class IncidentReport:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.medium
    status: IncidentStatus = IncidentStatus.open
    reported_by: str = ""
    assigned_to: str = ""
    resolution: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class RiskReport:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    risk_level: RiskLevel = RiskLevel.medium
    mitigated: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class AccessReviewSummary:
    org_id: UUID = field(default_factory=uuid4)
    total_reviews: int = 0
    completed_reviews: int = 0
    pending_reviews: int = 0
    last_review_date: datetime | None = None
