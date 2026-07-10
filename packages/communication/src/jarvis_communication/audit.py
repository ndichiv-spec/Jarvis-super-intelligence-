from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import AuditEntry


class AuditService:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    async def log(
        self,
        action: str,
        actor: str,
        target: str,
        *,
        details: dict[str, Any] | None = None,
        success: bool = True,
        ip_address: str | None = None,
        context: ExecutionContext | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            action=action,
            actor=actor,
            target=target,
            details=details or {},
            success=success,
            ip_address=ip_address,
        )
        self._entries.append(entry)
        return entry

    async def query(
        self,
        *,
        action: str | None = None,
        actor: str | None = None,
        target: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        success: bool | None = None,
        limit: int = 100,
        context: ExecutionContext | None = None,
    ) -> list[AuditEntry]:
        results: list[AuditEntry] = list(self._entries)
        if action:
            results = [e for e in results if e.action == action]
        if actor:
            results = [e for e in results if e.actor == actor]
        if target:
            results = [e for e in results if e.target == target]
        if since:
            results = [e for e in results if e.timestamp >= since]
        if until:
            results = [e for e in results if e.timestamp <= until]
        if success is not None:
            results = [e for e in results if e.success == success]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    async def get_by_id(
        self,
        entry_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> AuditEntry | None:
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    async def count_by_action(
        self,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.action] = counts.get(entry.action, 0) + 1
        return counts

    async def count_by_actor(
        self,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.actor] = counts.get(entry.actor, 0) + 1
        return counts

    @property
    def total_entries(self) -> int:
        return len(self._entries)
