from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_extensions.models import ExtensionHealth, ExtensionStatus


@dataclass(slots=True)
class InMemoryHealthMonitor:
    _health: dict[str, ExtensionHealth] = field(default_factory=dict)

    def record_activation(self, extension_id: str) -> ExtensionHealth:
        existing = self._health.get(extension_id)
        count = (existing.activation_count + 1) if existing is not None else 1
        health = ExtensionHealth(
            extension_id=extension_id,
            status=ExtensionStatus.ACTIVATED,
            is_healthy=True,
            activation_count=count,
            failure_count=existing.failure_count if existing is not None else 0,
            last_activated_at=datetime.now(UTC),
            last_failure_at=existing.last_failure_at if existing is not None else None,
            last_failure_message=existing.last_failure_message if existing is not None else "",
            total_runtime_ms=existing.total_runtime_ms if existing is not None else 0,
            performance_metadata=existing.performance_metadata if existing is not None else {},
        )
        self._health[extension_id] = health
        return health

    def record_failure(self, extension_id: str, message: str) -> ExtensionHealth:
        existing = self._health.get(extension_id)
        count = (existing.failure_count + 1) if existing is not None else 1
        health = ExtensionHealth(
            extension_id=extension_id,
            status=ExtensionStatus.FAILED,
            is_healthy=False,
            activation_count=existing.activation_count if existing is not None else 0,
            failure_count=count,
            last_activated_at=existing.last_activated_at if existing is not None else None,
            last_failure_at=datetime.now(UTC),
            last_failure_message=message,
            total_runtime_ms=existing.total_runtime_ms if existing is not None else 0,
            performance_metadata=existing.performance_metadata if existing is not None else {},
        )
        self._health[extension_id] = health
        return health

    def get_health(self, extension_id: str) -> ExtensionHealth | None:
        return self._health.get(extension_id)

    def list_unhealthy(self) -> tuple[ExtensionHealth, ...]:
        return tuple(h for h in self._health.values() if not h.is_healthy)

    def reset_health(self, extension_id: str) -> None:
        self._health.pop(extension_id, None)
