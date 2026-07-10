"""Analytics domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ReportCategory(StrEnum):
    usage = "usage"
    adoption = "adoption"
    performance = "performance"
    security = "security"
    automation = "automation"
    resource = "resource"


class ReportFormat(StrEnum):
    json = "json"
    csv = "csv"
    markdown = "markdown"


@dataclass(frozen=True, slots=True)
class ReportDefinition:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    category: ReportCategory = ReportCategory.usage
    format: ReportFormat = ReportFormat.json
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Report:
    id: UUID = field(default_factory=uuid4)
    definition_id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    generated_by: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    metric_name: str = ""
    org_id: UUID = field(default_factory=uuid4)
    value: float = 0.0
    unit: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class DashboardWidget:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    metric: str = ""
    visualization: str = "line"
    refresh_seconds: int = 60
