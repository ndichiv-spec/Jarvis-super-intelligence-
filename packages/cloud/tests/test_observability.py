"""Tests for Observability Platform."""

from jarvis_cloud.observability.platform import (
    ObservabilityPlatform,
    MetricType,
    LogLevel,
)


class TestObservabilityPlatform:
    def setup_method(self):
        self.platform = ObservabilityPlatform()

    def test_default_metrics(self):
        metrics = self.platform.get_metrics()
        assert "http_requests_total" in metrics
        assert "http_request_duration_seconds" in metrics

    def test_metric_types(self):
        metrics = self.platform.get_metrics()
        assert metrics["http_requests_total"].type == MetricType.counter
        assert metrics["http_request_duration_seconds"].type == MetricType.histogram
        assert metrics["active_connections"].type == MetricType.gauge

    def test_enable_tracing(self):
        self.platform.enable_tracing()
        assert self.platform.config.tracing.enabled is True
        assert self.platform.config.tracing.sampling_rate == 0.1

    def test_custom_tracing(self):
        self.platform.enable_tracing(endpoint="http://custom:4317", sampling_rate=0.5)
        assert self.platform.config.tracing.endpoint == "http://custom:4317"
        assert self.platform.config.tracing.sampling_rate == 0.5

    def test_prometheus_config(self):
        config = self.platform.generate_prometheus_config()
        assert "jarvis-api" in config
        assert "jarvis-services" in config
        assert "jarvis-infrastructure" in config
