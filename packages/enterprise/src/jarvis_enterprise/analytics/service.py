"""Analytics and reporting service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.analytics.models import (
    DashboardWidget,
    MetricSnapshot,
    Report,
    ReportCategory,
    ReportDefinition,
    ReportFormat,
)
from jarvis_enterprise.analytics.repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    def create_report_definition(
        self, name: str, category: ReportCategory = ReportCategory.usage,
        description: str = "", format: ReportFormat = ReportFormat.json,
    ) -> ReportDefinition:
        definition = ReportDefinition(name=name, description=description, category=category, format=format)
        self._repository.save_report_definition(definition)
        return definition

    def list_report_definitions(self) -> list[ReportDefinition]:
        return self._repository.list_report_definitions()

    def generate_report(
        self, definition_id: UUID, org_id: UUID, generated_by: str = "",
        data: dict | None = None,
    ) -> Report | None:
        definition = self._repository.get_report_definition(definition_id)
        if definition is None:
            return None
        report = Report(
            definition_id=definition_id, org_id=org_id,
            generated_by=generated_by, data=data or {},
        )
        self._repository.save_report(report)
        return report

    def list_reports(self, org_id: UUID, category: str | None = None) -> list[Report]:
        return self._repository.list_reports(org_id, category)

    def record_metric(self, metric_name: str, org_id: UUID, value: float, unit: str = "", labels: dict | None = None) -> MetricSnapshot:
        metric = MetricSnapshot(metric_name=metric_name, org_id=org_id, value=value, unit=unit, labels=labels or {})
        self._repository.save_metric(metric)
        return metric

    def query_metrics(self, metric_name: str, org_id: UUID) -> list[MetricSnapshot]:
        return self._repository.query_metrics(metric_name, org_id)

    def create_widget(self, title: str, metric: str, visualization: str = "line") -> DashboardWidget:
        widget = DashboardWidget(title=title, metric=metric, visualization=visualization)
        self._repository.save_widget(widget)
        return widget

    def list_widgets(self) -> list[DashboardWidget]:
        return self._repository.list_widgets()
