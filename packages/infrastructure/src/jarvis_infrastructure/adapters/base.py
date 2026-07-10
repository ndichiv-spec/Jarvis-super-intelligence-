from __future__ import annotations

from datetime import UTC, datetime

from jarvis_infrastructure.configuration import AdapterConfiguration
from jarvis_infrastructure.health import AdapterHealth, RecoveryStatus
from jarvis_infrastructure.metadata import AdapterMetadata


class BaseInfrastructureAdapter:
    def __init__(
        self,
        *,
        metadata: AdapterMetadata,
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._adapter_metadata = metadata
        self._dependencies = dependencies
        self._configuration: AdapterConfiguration | None = None
        self._running = False

    @property
    def adapter_metadata(self) -> AdapterMetadata:
        return self._adapter_metadata

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._dependencies

    @property
    def configuration(self) -> AdapterConfiguration | None:
        return self._configuration

    async def configure(self, configuration: AdapterConfiguration) -> None:
        self._configuration = configuration

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def health(self) -> AdapterHealth:
        return AdapterHealth(
            availability=self._running,
            connectivity=self._running,
            latency_ms=0.0 if self._running else None,
            version=self._adapter_metadata.version,
            compatibility=True,
            failures=0,
            recovery_status=RecoveryStatus.STABLE if self._running else RecoveryStatus.RECOVERING,
            checked_at=datetime.now(tz=UTC),
        )
