"""Health Monitor — per-subsystem status and consolidated platform health."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class HealthStatus(StrEnum):
    ready = "ready"
    warning = "warning"
    error = "error"
    unknown = "unknown"


@dataclass(frozen=True, slots=True)
class HealthCheck:
    subsystem: str = ""
    status: HealthStatus = HealthStatus.unknown
    message: str = ""
    latency_ms: float = 0.0
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class HealthReport:
    platform: HealthStatus = HealthStatus.unknown
    checks: tuple[HealthCheck, ...] = ()
    summary: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class HealthMonitor:
    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}

    def report(self, subsystem: str, status: HealthStatus, message: str = "", latency_ms: float = 0.0) -> HealthCheck:
        check = HealthCheck(
            subsystem=subsystem,
            status=status,
            message=message,
            latency_ms=latency_ms,
        )
        self._checks[subsystem] = check
        return check

    def get(self, subsystem: str) -> HealthCheck | None:
        return self._checks.get(subsystem)

    def get_report(self) -> HealthReport:
        checks = tuple(self._checks.values())
        if not checks:
            platform = HealthStatus.unknown
            summary = "No health checks reported"
        elif any(c.status == HealthStatus.error for c in checks):
            platform = HealthStatus.error
            summary = "Errors detected"
        elif any(c.status == HealthStatus.warning for c in checks):
            platform = HealthStatus.warning
            summary = "Warnings detected"
        elif any(c.status == HealthStatus.ready for c in checks):
            platform = HealthStatus.ready
            summary = "All systems ready"
        else:
            platform = HealthStatus.unknown
            summary = "Some subsystems not yet reported"
        return HealthReport(platform=platform, checks=checks, summary=summary)
