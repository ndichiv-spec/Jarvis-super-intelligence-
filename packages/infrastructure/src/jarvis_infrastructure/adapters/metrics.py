from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from datetime import timedelta
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


class Metrics(Protocol):
    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None: ...

    def timing(
        self,
        metric_name: str,
        duration: timedelta,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...

class PrometheusClient(Protocol):
    def increment(self, metric_name: str, value: int, tags: Mapping[str, str]) -> None: ...

    def observe(self, metric_name: str, value: float, tags: Mapping[str, str]) -> None: ...


class OpenTelemetryMeter(Protocol):
    def add_counter(self, metric_name: str, value: int, attributes: Mapping[str, str]) -> None: ...

    def record_histogram(
        self, metric_name: str, value: float, attributes: Mapping[str, str]
    ) -> None: ...


class InMemoryMetricsAdapter(BaseInfrastructureAdapter, Metrics):
    def __init__(self) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="metrics.in_memory",
                version="1.0.0",
                provider="in-memory",
                capabilities=("metrics", "counters", "timings"),
                configuration_profile="default",
                compatibility=("metrics:v1",),
            )
        )
        self._counters: dict[str, int] = defaultdict(int)
        self._timings_ms: dict[str, list[float]] = defaultdict(list)

    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None:
        key = _metric_key(metric_name, tags)
        self._counters[key] += 1

    def timing(
        self,
        metric_name: str,
        duration: timedelta,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        key = _metric_key(metric_name, tags)
        self._timings_ms[key].append(duration.total_seconds() * 1000.0)

    def counters(self) -> Mapping[str, int]:
        return dict(self._counters)

    def timings(self) -> Mapping[str, tuple[float, ...]]:
        return {name: tuple(values) for name, values in self._timings_ms.items()}


class PrometheusMetricsAdapter(BaseInfrastructureAdapter, Metrics):
    def __init__(self, *, client: PrometheusClient | None = None) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="metrics.prometheus",
                version="1.0.0",
                provider="prometheus",
                capabilities=("metrics", "counters", "histograms"),
                configuration_profile="default",
                compatibility=("metrics:v1",),
            )
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("Prometheus client is required.")
        await super().start()

    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None:
        if self._client is None:
            raise RuntimeError("Prometheus client is not configured.")
        self._client.increment(metric_name, 1, dict(tags or {}))

    def timing(
        self,
        metric_name: str,
        duration: timedelta,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        if self._client is None:
            raise RuntimeError("Prometheus client is not configured.")
        self._client.observe(metric_name, duration.total_seconds(), dict(tags or {}))


class OpenTelemetryMetricsAdapter(BaseInfrastructureAdapter, Metrics):
    def __init__(self, *, meter: OpenTelemetryMeter | None = None) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="metrics.opentelemetry",
                version="1.0.0",
                provider="opentelemetry",
                capabilities=("metrics", "counters", "histograms"),
                configuration_profile="default",
                compatibility=("metrics:v1",),
            )
        )
        self._meter = meter

    async def start(self) -> None:
        if self._meter is None:
            raise RuntimeError("OpenTelemetry meter is required.")
        await super().start()

    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None:
        if self._meter is None:
            raise RuntimeError("OpenTelemetry meter is not configured.")
        self._meter.add_counter(metric_name, 1, dict(tags or {}))

    def timing(
        self,
        metric_name: str,
        duration: timedelta,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None:
        if self._meter is None:
            raise RuntimeError("OpenTelemetry meter is not configured.")
        self._meter.record_histogram(metric_name, duration.total_seconds(), dict(tags or {}))


def _metric_key(metric_name: str, tags: Mapping[str, str] | None) -> str:
    if not tags:
        return metric_name
    rendered_tags = ",".join(f"{key}={value}" for key, value in sorted(tags.items()))
    return f"{metric_name}|{rendered_tags}"
