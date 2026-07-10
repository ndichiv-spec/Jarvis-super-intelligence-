"""Deployment Manager - orchestrate versioned, repeatable deployments."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from jarvis_cloud.deployment.profiles import (
    DeploymentEnvironment,
    DeploymentProfile,
    ProfileLoader,
)
from jarvis_cloud.release.manager import ReleaseManager


class DeploymentStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    rolled_back = "rolled_back"


@dataclass(frozen=True)
class DeploymentRecord:
    id: str
    profile_name: str
    environment: DeploymentEnvironment
    version: str
    status: DeploymentStatus
    started_at: datetime
    completed_at: datetime | None = None
    services: dict[str, bool] = field(default_factory=dict)
    error: str | None = None


class DeploymentManager:
    def __init__(self, release_manager: ReleaseManager | None = None) -> None:
        self._profile_loader = ProfileLoader()
        self._release_manager = release_manager or ReleaseManager()
        self._history: list[DeploymentRecord] = []
        self._current: DeploymentRecord | None = None

    @property
    def current(self) -> DeploymentRecord | None:
        return self._current

    @property
    def history(self) -> list[DeploymentRecord]:
        return list(self._history)

    def plan(self, profile_name: str, version: str) -> dict[str, Any]:
        profile = self._profile_loader.load(profile_name)
        services = {name: svc.replicas for name, svc in profile.services.items()}
        return {
            "profile": profile_name,
            "environment": profile.environment.value,
            "version": version,
            "services": services,
            "infrastructure": {
                "postgres": profile.infrastructure.postgres is not None,
                "redis": profile.infrastructure.redis is not None,
                "qdrant": profile.infrastructure.qdrant is not None,
            },
        }

    def deploy(self, profile_name: str, version: str) -> DeploymentRecord:
        profile = self._profile_loader.load(profile_name)
        record = DeploymentRecord(
            id=f"deploy-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            profile_name=profile_name,
            environment=profile.environment,
            version=version,
            status=DeploymentStatus.in_progress,
            started_at=datetime.now(timezone.utc),
        )
        self._current = record
        self._history.append(record)
        return record

    def complete(self, record_id: str, status: DeploymentStatus, error: str | None = None) -> DeploymentRecord:
        updated = DeploymentRecord(
            id=record_id,
            profile_name=self._current.profile_name if self._current else "",
            environment=self._current.environment if self._current else DeploymentEnvironment.development,
            version=self._current.version if self._current else "",
            status=status,
            started_at=self._current.started_at if self._current else datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            services=self._current.services if self._current else {},
            error=error,
        )
        self._history = [
            updated if r.id == record_id else r
            for r in self._history
        ]
        self._current = updated
        return updated

    def rollback(self, record_id: str) -> DeploymentRecord:
        return self.complete(record_id, DeploymentStatus.rolled_back)

    def list_deployments(self, environment: str | None = None) -> list[DeploymentRecord]:
        if environment is None:
            return self._history
        return [d for d in self._history if d.environment.value == environment]

    def validate(self, profile_name: str) -> list[str]:
        issues: list[str] = []
        try:
            profile = self._profile_loader.load(profile_name)
        except ValueError as e:
            return [str(e)]
        for name, svc in profile.services.items():
            if not svc.image:
                issues.append(f"Service {name}: missing image")
            if svc.replicas < 1:
                issues.append(f"Service {name}: replicas must be >= 1")
            if not svc.health_check:
                issues.append(f"Service {name}: missing health check")
        return issues
