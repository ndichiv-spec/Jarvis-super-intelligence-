"""Tests for Analytics & Reporting."""

from uuid import uuid4

from jarvis_enterprise.analytics.models import (
    DashboardWidget,
    MetricSnapshot,
    Report,
    ReportCategory,
    ReportDefinition,
    ReportFormat,
)
from jarvis_enterprise.analytics.repository import AnalyticsRepository
from jarvis_enterprise.analytics.service import AnalyticsService


class InMemoryAnalyticsRepo:
    def __init__(self):
        self._definitions: dict = {}
        self._reports: list = []
        self._metrics: list = []
        self._widgets: dict = {}

    def save_report_definition(self, definition) -> None:
        self._definitions[definition.id] = definition

    def get_report_definition(self, definition_id) -> ReportDefinition | None:
        return self._definitions.get(definition_id)

    def list_report_definitions(self) -> list[ReportDefinition]:
        return list(self._definitions.values())

    def save_report(self, report) -> None:
        self._reports.append(report)

    def list_reports(self, org_id, category=None) -> list[Report]:
        return [r for r in self._reports if r.org_id == org_id]

    def save_metric(self, metric) -> None:
        self._metrics.append(metric)

    def query_metrics(self, metric_name, org_id) -> list[MetricSnapshot]:
        return [m for m in self._metrics if m.metric_name == metric_name and m.org_id == org_id]

    def save_widget(self, widget) -> None:
        self._widgets[widget.id] = widget

    def list_widgets(self) -> list[DashboardWidget]:
        return list(self._widgets.values())


class TestAnalyticsService:
    def setup_method(self):
        self.repo = AnalyticsService(InMemoryAnalyticsRepo())

    def test_create_report_definition(self):
        definition = self.repo.create_report_definition("Usage Report", ReportCategory.usage)
        assert definition.name == "Usage Report"
        assert definition.category == ReportCategory.usage

    def test_generate_report(self):
        definition = self.repo.create_report_definition("Test Report", ReportCategory.performance)
        report = self.repo.generate_report(definition.id, uuid4(), "admin", {"data": "value"})
        assert report is not None
        assert report.data["data"] == "value"

    def test_generate_report_nonexistent_definition(self):
        report = self.repo.generate_report(uuid4(), uuid4())
        assert report is None

    def test_record_metric(self):
        metric = self.repo.record_metric("api_latency", uuid4(), 42.5, "ms", {"service": "api"})
        assert metric.value == 42.5
        assert metric.unit == "ms"

    def test_query_metrics(self):
        org_id = uuid4()
        self.repo.record_metric("cpu_usage", org_id, 65.0)
        self.repo.record_metric("cpu_usage", org_id, 70.0)
        results = self.repo.query_metrics("cpu_usage", org_id)
        assert len(results) == 2

    def test_create_widget(self):
        widget = self.repo.create_widget("CPU Usage", "cpu_usage", "gauge")
        assert widget.title == "CPU Usage"
        assert widget.visualization == "gauge"

    def test_list_report_definitions(self):
        self.repo.create_report_definition("R1", ReportCategory.usage)
        self.repo.create_report_definition("R2", ReportCategory.security)
        assert len(self.repo.list_report_definitions()) == 2
