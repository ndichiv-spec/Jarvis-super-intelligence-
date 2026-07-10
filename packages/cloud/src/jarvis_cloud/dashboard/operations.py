"""Operations Dashboard - operational visibility into deployments, health, and resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class ServiceStatus(StrEnum):
    running = "running"
    degraded = "degraded"
    stopped = "stopped"
    unknown = "unknown"


@dataclass(frozen=True)
class ServiceHealthSnapshot:
    service: str
    status: ServiceStatus
    replicas: int
    available_replicas: int
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class DeploymentSummary:
    environment: str
    version: str
    services: int
    healthy_services: int
    last_deployed: datetime | None = None


@dataclass(frozen=True)
class OperationsDashboardState:
    services: dict[str, ServiceHealthSnapshot] = field(default_factory=dict)
    deployments: list[DeploymentSummary] = field(default_factory=list)
    scaling_events: list[dict[str, Any]] = field(default_factory=list)
    alerts: list[dict[str, Any]] = field(default_factory=list)
    resource_summary: dict[str, Any] = field(default_factory=dict)


class OperationsDashboard:
    def __init__(self) -> None:
        self._state = OperationsDashboardState()

    @property
    def state(self) -> OperationsDashboardState:
        return self._state

    def update_service_health(self, service: str, status: ServiceStatus, replicas: int, available: int) -> None:
        snapshot = ServiceHealthSnapshot(
            service=service,
            status=status,
            replicas=replicas,
            available_replicas=available,
        )
        self._state = OperationsDashboardState(
            services={**self._state.services, service: snapshot},
            deployments=self._state.deployments,
            scaling_events=self._state.scaling_events,
            alerts=self._state.alerts,
            resource_summary=self._state.resource_summary,
        )

    def add_deployment(self, environment: str, version: str, services: int, healthy: int) -> None:
        summary = DeploymentSummary(
            environment=environment,
            version=version,
            services=services,
            healthy_services=healthy,
            last_deployed=datetime.now(timezone.utc),
        )
        self._state = OperationsDashboardState(
            services=self._state.services,
            deployments=[summary] + self._state.deployments,
            scaling_events=self._state.scaling_events,
            alerts=self._state.alerts,
            resource_summary=self._state.resource_summary,
        )

    def add_alert(self, severity: str, title: str, message: str) -> None:
        alert = {"severity": severity, "title": title, "message": message, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._state = OperationsDashboardState(
            services=self._state.services,
            deployments=self._state.deployments,
            scaling_events=self._state.scaling_events,
            alerts=[alert] + self._state.alerts,
            resource_summary=self._state.resource_summary,
        )

    def summary(self) -> dict[str, Any]:
        total = len(self._state.services)
        healthy = sum(1 for s in self._state.services.values() if s.status == ServiceStatus.running)
        return {
            "services": {"total": total, "healthy": healthy, "degraded": total - healthy},
            "deployments": len(self._state.deployments),
            "active_alerts": len([a for a in self._state.alerts if a["severity"] in ("critical", "warning")]),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
