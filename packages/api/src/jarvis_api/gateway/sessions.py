from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jarvis_api.gateway.types import ProtocolName


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    identity_id: str | None
    workspace_id: str | None
    protocol: ProtocolName
    protocol_metadata: dict[str, Any]
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    heartbeat_interval_seconds: int = 30

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at


class SessionManager:
    def __init__(self, *, default_timeout: timedelta = timedelta(minutes=30)) -> None:
        self._default_timeout = default_timeout
        self._sessions: dict[str, SessionRecord] = {}

    def open_or_touch(
        self,
        *,
        session_id: str | None,
        identity_id: str | None,
        workspace_id: str | None,
        protocol: ProtocolName,
        metadata: Mapping[str, Any] | None = None,
        timeout_policy: timedelta | None = None,
        heartbeat_interval_seconds: int = 30,
    ) -> SessionRecord:
        current_time = datetime.now(tz=UTC)
        resolved_timeout = timeout_policy or self._default_timeout
        resolved_session_id = session_id or str(uuid4())

        existing = self._sessions.get(resolved_session_id)
        if existing is not None:
            existing.last_seen_at = current_time
            existing.expires_at = current_time + resolved_timeout
            if metadata:
                existing.protocol_metadata.update(dict(metadata))
            return existing

        record = SessionRecord(
            session_id=resolved_session_id,
            identity_id=identity_id,
            workspace_id=workspace_id,
            protocol=protocol,
            protocol_metadata=dict(metadata or {}),
            created_at=current_time,
            last_seen_at=current_time,
            expires_at=current_time + resolved_timeout,
            heartbeat_interval_seconds=heartbeat_interval_seconds,
        )
        self._sessions[resolved_session_id] = record
        return record

    def get(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def heartbeat(
        self,
        session_id: str,
        *,
        timeout_policy: timedelta | None = None,
    ) -> SessionRecord | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None

        current_time = datetime.now(tz=UTC)
        resolved_timeout = timeout_policy or self._default_timeout
        session.last_seen_at = current_time
        session.expires_at = current_time + resolved_timeout
        return session

    def close(self, session_id: str) -> bool:
        removed = self._sessions.pop(session_id, None)
        return removed is not None

    def expire_stale(self, *, current_time: datetime | None = None) -> tuple[str, ...]:
        now = current_time or datetime.now(tz=UTC)
        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if session.is_expired(now)
        ]
        for session_id in expired:
            self._sessions.pop(session_id, None)
        return tuple(expired)

    def active_sessions(self) -> tuple[SessionRecord, ...]:
        return tuple(sorted(self._sessions.values(), key=lambda session: session.session_id))
