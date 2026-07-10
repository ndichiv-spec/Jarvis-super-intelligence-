"""Enterprise observability service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.observability.models import (
    PerformanceTrend,
    PlatformHealth,
    ServiceAvailability,
    ServiceHealth,
    ServiceStatus,
    UsageMetric,
)


class EnterpriseObservabilityService:
    def __init__(self) -> None:
        self._health: dict[str, ServiceHealth] = {}
        self._usage: list[UsageMetric] = []
        self._availability: dict[str, ServiceAvailability] = {}

    def report_service_health(self, service_name: str, status: ServiceStatus, latency_ms: float = 0.0) -> ServiceHealth:
        health = ServiceHealth(service_name=service_name, status=status, latency_ms=latency_ms)
        self._health[service_name] = health
        return health

    def get_platform_health(self, org_id: UUID) -> PlatformHealth:
        services = tuple(self._health.values())
        total = len(services)
        healthy = sum(1 for s in services if s.status == ServiceStatus.healthy)
        degraded = sum(1 for s in services if s.status == ServiceStatus.degraded)
        unhealthy_count = sum(1 for s in services if s.status == ServiceStatus.unhealthy)
        if unhealthy_count > 0:
            overall = ServiceStatus.unhealthy
        elif degraded > 0:
            overall = ServiceStatus.degraded
        else:
            overall = ServiceStatus.healthy
        return PlatformHealth(
            org_id=org_id, services=services,
            total_services=total, healthy_services=healthy,
            degraded_services=degraded, unhealthy_services=unhealthy_count,
            overall_status=overall,
        )

    def record_usage(self, metric_name: str, org_id: UUID, total: int, by_service: dict[str, int] | None = None) -> UsageMetric:
        metric = UsageMetric(
            metric_name=metric_name, org_id=org_id, total=total,
            by_service=by_service or {},
            period_end=datetime.now(timezone.utc),
        )
        self._usage.append(metric)
        return metric

    def get_usage(self, org_id: UUID, metric_name: str | None = None) -> list[UsageMetric]:
        return [
            m for m in self._usage
            if m.org_id == org_id and (metric_name is None or m.metric_name == metric_name)
        ]

    def record_availability(self, service_name: str, availability_pct: float, downtime_minutes: int = 0) -> ServiceAvailability:
        av = ServiceAvailability(
            service_name=service_name,
            availability_pct=availability_pct,
            downtime_minutes=downtime_minutes,
        )
        self._availability[service_name] = av
        return av

    def get_availability_report(self) -> list[ServiceAvailability]:
        return list(self._availability.values())

    def get_performance_trend(self, metric_name: str) -> PerformanceTrend | None:
        relevant = [m for m in self._usage if m.metric_name == metric_name]
        if len(relevant) < 2:
            return None
        current = relevant[-1]
        previous = relevant[-2]
        change = current.total - previous.total
        pct = (change / previous.total * 100) if previous.total > 0 else 0.0
        trend = "increasing" if pct > 5 else ("decreasing" if pct < -5 else "stable")
        return PerformanceTrend(
            metric_name=metric_name, current_value=float(current.total),
            previous_value=float(previous.total), change_pct=pct, trend=trend,
        )
