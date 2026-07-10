from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


class SyncStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class SyncState:
    document_id: str
    status: str
    last_synced: datetime | None = None
    remote_version: int = 0
    local_version: int = 0
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SyncResult:
    document_id: str
    success: bool
    new_version: int
    conflicts: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None


class SyncEngine(Protocol):
    def sync(self, document_id: str, local_version: int, remote_version: int) -> SyncResult: ...
    def resolve_conflict(self, document_id: str, resolution: str) -> SyncResult: ...


class DefaultSyncEngine:
    def __init__(self) -> None:
        self._states: dict[str, SyncState] = {}

    def sync(self, document_id: str, local_version: int, remote_version: int) -> SyncResult:
        current = self._states.get(document_id)
        if current and current.status == SyncStatus.CONFLICT:
            return SyncResult(
                document_id=document_id,
                success=False,
                new_version=local_version,
                conflicts=("pending_conflict_resolution",),
                error="Conflict must be resolved before syncing",
            )
        if remote_version > local_version:
            self._states[document_id] = SyncState(
                document_id=document_id,
                status=SyncStatus.COMPLETED,
                last_synced=datetime.now(UTC),
                remote_version=remote_version,
                local_version=remote_version,
            )
            return SyncResult(
                document_id=document_id,
                success=True,
                new_version=remote_version,
            )
        if local_version > remote_version:
            self._states[document_id] = SyncState(
                document_id=document_id,
                status=SyncStatus.COMPLETED,
                last_synced=datetime.now(UTC),
                remote_version=local_version,
                local_version=local_version,
            )
            return SyncResult(
                document_id=document_id,
                success=True,
                new_version=local_version,
            )
        return SyncResult(
            document_id=document_id,
            success=True,
            new_version=local_version,
        )

    def resolve_conflict(self, document_id: str, resolution: str) -> SyncResult:
        current = self._states.get(document_id)
        if not current or current.status != SyncStatus.CONFLICT:
            return SyncResult(
                document_id=document_id,
                success=False,
                new_version=current.local_version if current else 0,
                error="No conflict to resolve",
            )
        resolved_version = max(current.local_version, current.remote_version)
        self._states[document_id] = SyncState(
            document_id=document_id,
            status=SyncStatus.COMPLETED,
            last_synced=datetime.now(UTC),
            remote_version=resolved_version,
            local_version=resolved_version,
        )
        return SyncResult(
            document_id=document_id,
            success=True,
            new_version=resolved_version,
        )

    def get_state(self, document_id: str) -> SyncState | None:
        return self._states.get(document_id)
