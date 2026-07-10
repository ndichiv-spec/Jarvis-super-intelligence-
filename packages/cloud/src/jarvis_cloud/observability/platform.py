"""Observability Platform - metrics, logging, tracing integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MetricType(StrEnum):
    counter = "counter"
    gauge = "gauge"
    histogram = "histogram"
    summary = "summary"


class LogLevel(StrEnum):
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"
    fatal = "fatal"


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    type: MetricType
    description: str
    unit: str = ""
    labels: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LogConfig:
    level: LogLevel = LogLevel.info
    format: str = "json"
    output: str = "stdout"
    correlation_id: bool = True


@dataclass(frozen=True)
class TraceConfig:
    enabled: bool = False
    sampling_rate: float = 0.1
    exporter: str = "otlp"
    endpoint: str = "http://otel-collector:4317"


@dataclass(frozen=True)
class ObservabilityConfig:
    metrics: dict[str, MetricDefinition] = field(default_factory=dict)
    logging: LogConfig = field(default_factory=LogConfig)
    tracing: TraceConfig = field(default_factory=TraceConfig)
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"


DEFAULT_METRICS: dict[str, MetricDefinition] = {
    "http_requests_total": MetricDefinition(
        name="http_requests_total",
        type=MetricType.counter,
        description="Total HTTP requests",
        labels=["method", "path", "status"],
    ),
    "http_request_duration_seconds": MetricDefinition(
        name="http_request_duration_seconds",
        type=MetricType.histogram,
        description="HTTP request duration in seconds",
        unit="s",
        labels=["method", "path"],
    ),
    "active_connections": MetricDefinition(
        name="active_connections",
        type=MetricType.gauge,
        description="Active connections",
    ),
    "queue_depth": MetricDefinition(
        name="queue_depth",
        type=MetricType.gauge,
        description="Current queue depth",
    ),
    "memory_usage_bytes": MetricDefinition(
        name="memory_usage_bytes",
        type=MetricType.gauge,
        description="Memory usage in bytes",
        unit="bytes",
    ),
    "cpu_usage_percent": MetricDefinition(
        name="cpu_usage_percent",
        type=MetricType.gauge,
        description="CPU usage percentage",
        unit="percent",
    ),
    "ai_requests_total": MetricDefinition(
        name="ai_requests_total",
        type=MetricType.counter,
        description="Total AI provider requests",
        labels=["provider", "model"],
    ),
    "ai_request_duration_seconds": MetricDefinition(
        name="ai_request_duration_seconds",
        type=MetricType.histogram,
        description="AI request duration",
        unit="s",
        labels=["provider", "model"],
    ),
    "workflow_runs_total": MetricDefinition(
        name="workflow_runs_total",
        type=MetricType.counter,
        description="Total workflow runs",
        labels=["status"],
    ),
    "memory_operations_total": MetricDefinition(
        name="memory_operations_total",
        type=MetricType.counter,
        description="Total memory operations",
        labels=["operation"],
    ),
}


class ObservabilityPlatform:
    def __init__(self) -> None:
        self._config = ObservabilityConfig(metrics=DEFAULT_METRICS)

    @property
    def config(self) -> ObservabilityConfig:
        return self._config

    def get_metrics(self) -> dict[str, MetricDefinition]:
        return dict(self._config.metrics)

    def enable_tracing(self, endpoint: str = "http://otel-collector:4317", sampling_rate: float = 0.1) -> None:
        self._config = ObservabilityConfig(
            metrics=self._config.metrics,
            logging=self._config.logging,
            tracing=TraceConfig(enabled=True, sampling_rate=sampling_rate, endpoint=endpoint),
        )

    def generate_prometheus_config(self) -> str:
        return """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jarvis-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: api
        action: keep
      - source_labels: [__address__]
        action: replace
        regex: ([^:]+)(?::\\d+)?
        replacement: $1:8000
        target_label: __address__

  - job_name: 'jarvis-services'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: (brain|ai|memory|knowledge|automation|agents|orchestration)
        action: keep
      - source_labels: [__address__]
        action: replace
        regex: ([^:]+)(?::\\d+)?
        replacement: $1:8000
        target_label: __address__

  - job_name: 'jarvis-infrastructure'
    static_configs:
      - targets: ['postgres:9187', 'redis:9121']
"""
