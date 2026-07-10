from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class RecoveryStatus(StrEnum):
    STABLE = "stable"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class AdapterHealth:
    availability: bool
    connectivity: bool
    latency_ms: float | None
    version: str
    compatibility: bool
    failures: int
    recovery_status: RecoveryStatus
    checked_at: datetime


class AdapterHealthMonitor:
    def __init__(self) -> None:
        self._records: dict[str, AdapterHealth] = {}

    def update(self, adapter_id: str, health: AdapterHealth) -> None:
        self._records[adapter_id] = health

    def mark_failure(self, adapter_id: str, *, version: str = "unknown") -> AdapterHealth:
        previous = self._records.get(adapter_id)
        failures = 1 if previous is None else previous.failures + 1
        recovery_status = RecoveryStatus.RECOVERING if failures <= 3 else RecoveryStatus.FAILED
        health = AdapterHealth(
            availability=False,
            connectivity=False,
            latency_ms=None,
            version=version,
            compatibility=False,
            failures=failures,
            recovery_status=recovery_status,
            checked_at=datetime.now(tz=UTC),
        )
        self._records[adapter_id] = health
        return health

    def get(self, adapter_id: str) -> AdapterHealth | None:
        return self._records.get(adapter_id)

    def snapshot(self) -> dict[str, AdapterHealth]:
        return dict(self._records)
