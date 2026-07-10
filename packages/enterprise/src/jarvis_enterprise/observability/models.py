"""Observability domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ServiceStatus(StrEnum):
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"
    unknown = "unknown"


@dataclass(frozen=True, slots=True)
class ServiceHealth:
    service_name: str = ""
    status: ServiceStatus = ServiceStatus.unknown
    latency_ms: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PlatformHealth:
    org_id: UUID = field(default_factory=uuid4)
    services: tuple[ServiceHealth, ...] = ()
    total_services: int = 0
    healthy_services: int = 0
    degraded_services: int = 0
    unhealthy_services: int = 0
    overall_status: ServiceStatus = ServiceStatus.healthy


@dataclass(frozen=True, slots=True)
class ServiceAvailability:
    service_name: str = ""
    availability_pct: float = 100.0
    measured_hours: int = 0
    downtime_minutes: int = 0


@dataclass(frozen=True, slots=True)
class UsageMetric:
    metric_name: str = ""
    org_id: UUID = field(default_factory=uuid4)
    total: int = 0
    by_service: dict[str, int] = field(default_factory=dict)
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PerformanceTrend:
    metric_name: str = ""
    current_value: float = 0.0
    previous_value: float = 0.0
    change_pct: float = 0.0
    trend: str = "stable"
