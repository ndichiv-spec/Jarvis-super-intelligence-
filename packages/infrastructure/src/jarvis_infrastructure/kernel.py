from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from jarvis_infrastructure.configuration import (
    AdapterConfiguration,
    ConfigurationLoader,
    InfrastructureConfiguration,
)
from jarvis_infrastructure.health import AdapterHealth, AdapterHealthMonitor
from jarvis_infrastructure.metadata import AdapterMetadata, AdapterStatus


@runtime_checkable
class InfrastructureAdapter(Protocol):
    @property
    def adapter_metadata(self) -> AdapterMetadata: ...

    @property
    def dependencies(self) -> tuple[str, ...]: ...

    async def configure(self, configuration: AdapterConfiguration) -> None: ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def health(self) -> AdapterHealth: ...


class InfrastructureKernel:
    def __init__(self, *, health_monitor: AdapterHealthMonitor | None = None) -> None:
        self._health_monitor = health_monitor or AdapterHealthMonitor()
        self._adapters: dict[str, InfrastructureAdapter] = {}
        self._metadata: dict[str, AdapterMetadata] = {}
        self._configuration: InfrastructureConfiguration = InfrastructureConfiguration.create(
            profile="default"
        )
        self._started: list[str] = []

    def register(self, adapter: InfrastructureAdapter) -> None:
        adapter_id = adapter.adapter_metadata.identifier
        if adapter_id in self._adapters:
            raise ValueError(f"Adapter '{adapter_id}' already registered.")
        self._adapters[adapter_id] = adapter
        self._metadata[adapter_id] = adapter.adapter_metadata.with_status(AdapterStatus.REGISTERED)

    def resolve(self, adapter_id: str) -> InfrastructureAdapter:
        if adapter_id not in self._adapters:
            raise KeyError(f"Unknown adapter '{adapter_id}'.")
        return self._adapters[adapter_id]

    def metadata_snapshot(self) -> Mapping[str, AdapterMetadata]:
        return dict(self._metadata)

    def health_snapshot(self) -> dict[str, AdapterHealth]:
        return self._health_monitor.snapshot()

    def load_configuration(
        self,
        loader: ConfigurationLoader,
        *,
        profile: str | None = None,
    ) -> InfrastructureConfiguration:
        self._configuration = loader.load(profile=profile)
        return self._configuration

    async def start(self) -> None:
        order = self._resolve_order()
        for adapter_id in order:
            adapter = self._adapters[adapter_id]
            config = self._configuration.adapters.get(adapter_id)
            if config is None:
                config = AdapterConfiguration.create(
                    identifier=adapter_id,
                    provider=adapter.adapter_metadata.provider,
                    profile=self._configuration.profile,
                    dependencies=adapter.dependencies,
                )
            if not config.enabled:
                self._metadata[adapter_id] = self._metadata[adapter_id].with_status(
                    AdapterStatus.STOPPED
                )
                continue

            self._metadata[adapter_id] = self._metadata[adapter_id].with_status(
                AdapterStatus.CONFIGURED
            )
            await adapter.configure(config)
            self._metadata[adapter_id] = self._metadata[adapter_id].with_status(
                AdapterStatus.STARTING
            )
            try:
                await adapter.start()
                health = await adapter.health()
                self._health_monitor.update(adapter_id, health)
                status = AdapterStatus.RUNNING if health.availability else AdapterStatus.DEGRADED
                self._metadata[adapter_id] = self._metadata[adapter_id].with_status(status)
                self._started.append(adapter_id)
            except Exception:
                self._health_monitor.mark_failure(
                    adapter_id,
                    version=self._metadata[adapter_id].version,
                )
                self._metadata[adapter_id] = self._metadata[adapter_id].with_status(
                    AdapterStatus.FAILED
                )
                raise

    async def stop(self) -> None:
        while self._started:
            adapter_id = self._started.pop()
            adapter = self._adapters[adapter_id]
            await adapter.stop()
            self._metadata[adapter_id] = self._metadata[adapter_id].with_status(
                AdapterStatus.STOPPED
            )

    def _resolve_order(self) -> list[str]:
        dependencies: dict[str, set[str]] = {}
        for adapter_id, adapter in self._adapters.items():
            config_deps = self._configuration.adapters.get(adapter_id)
            configured = set(config_deps.dependencies if config_deps is not None else ())
            declared = set(adapter.dependencies)
            all_dependencies = configured | declared
            for dependency in all_dependencies:
                if dependency not in self._adapters:
                    raise ValueError(
                        f"Adapter '{adapter_id}' depends on unknown adapter '{dependency}'."
                    )
            dependencies[adapter_id] = all_dependencies

        order: list[str] = []
        ready = [identifier for identifier, deps in dependencies.items() if not deps]
        remaining = dict(dependencies)

        while ready:
            current = ready.pop()
            order.append(current)
            for adapter_id, deps in list(remaining.items()):
                if current in deps:
                    deps.remove(current)
                if not deps and adapter_id not in order and adapter_id not in ready:
                    ready.append(adapter_id)
            remaining.pop(current, None)

        if remaining:
            cycle_ids = ", ".join(sorted(remaining.keys()))
            raise ValueError(f"Circular adapter dependency detected: {cycle_ids}")
        return order
