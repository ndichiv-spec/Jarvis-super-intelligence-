"""Backup & Recovery Manager - backup strategies and restoration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class BackupStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class BackupTarget(StrEnum):
    postgres = "postgres"
    redis = "redis"
    qdrant = "qdrant"
    minio = "minio"
    config = "config"
    secrets = "secrets"
    filesystem = "filesystem"


class RetentionPolicy(StrEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


@dataclass(frozen=True)
class BackupJob:
    id: str
    target: BackupTarget
    started_at: datetime
    status: BackupStatus = BackupStatus.pending
    size_bytes: int | None = None
    path: str | None = None
    error: str | None = None
    completed_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BackupSchedule:
    target: BackupTarget
    cron: str
    retention: RetentionPolicy
    retention_count: int = 7
    compression: bool = True
    encryption: bool = True


@dataclass(frozen=True)
class BackupStrategy:
    schedules: list[BackupSchedule] = field(default_factory=list)
    global_encryption: bool = True
    global_compression: bool = True
    storage_path: str = "/data/backups"
    verify_after_backup: bool = True
    max_parallel_jobs: int = 3


DEFAULT_BACKUP_STRATEGY = BackupStrategy(
    schedules=[
        BackupSchedule(target=BackupTarget.postgres, cron="0 2 * * *", retention=RetentionPolicy.daily, retention_count=7),
        BackupSchedule(target=BackupTarget.redis, cron="0 3 * * *", retention=RetentionPolicy.daily, retention_count=3),
        BackupSchedule(target=BackupTarget.qdrant, cron="0 4 * * *", retention=RetentionPolicy.daily, retention_count=7),
        BackupSchedule(target=BackupTarget.minio, cron="0 5 * * *", retention=RetentionPolicy.weekly, retention_count=4),
        BackupSchedule(target=BackupTarget.config, cron="0 */6 * * *", retention=RetentionPolicy.daily, retention_count=30),
    ],
)


class BackupManager:
    def __init__(self, strategy: BackupStrategy | None = None) -> None:
        self._strategy = strategy or DEFAULT_BACKUP_STRATEGY
        self._jobs: list[BackupJob] = []
        self._history: list[BackupJob] = []

    @property
    def strategy(self) -> BackupStrategy:
        return self._strategy

    @property
    def jobs(self) -> list[BackupJob]:
        return list(self._jobs)

    @property
    def history(self) -> list[BackupJob]:
        return list(self._history)

    def create_job(self, target: BackupTarget) -> BackupJob:
        job = BackupJob(
            id=f"backup-{target.value}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            target=target,
            started_at=datetime.now(timezone.utc),
        )
        self._jobs.append(job)
        return job

    def complete_job(self, job_id: str, status: BackupStatus, path: str | None = None, error: str | None = None) -> BackupJob:
        updated = BackupJob(
            id=job_id,
            target=self._find_job(job_id).target,
            started_at=self._find_job(job_id).started_at,
            status=status,
            path=path,
            error=error,
            completed_at=datetime.now(timezone.utc),
            metadata=self._find_job(job_id).metadata,
        )
        self._jobs = [j for j in self._jobs if j.id != job_id]
        self._history.append(updated)
        return updated

    def _find_job(self, job_id: str) -> BackupJob:
        for j in self._jobs:
            if j.id == job_id:
                return j
        raise ValueError(f"Backup job not found: {job_id}")

    def list_history(self, target: BackupTarget | None = None, limit: int = 20) -> list[BackupJob]:
        items = self._history if target is None else [j for j in self._history if j.target == target]
        return sorted(items, key=lambda j: j.started_at, reverse=True)[:limit]

    def verify(self) -> list[str]:
        issues: list[str] = []
        if not self._strategy.schedules:
            issues.append("No backup schedules defined")
        targets = {s.target for s in self._strategy.schedules}
        for t in BackupTarget:
            if t not in targets:
                issues.append(f"No backup schedule for target: {t.value}")
        return issues
