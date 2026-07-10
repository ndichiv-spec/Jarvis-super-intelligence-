"""Compliance domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ExportFormat(StrEnum):
    json = "json"
    csv = "csv"
    parquet = "parquet"


class ComplianceFramework(StrEnum):
    gdpr = "gdpr"
    soc2 = "soc2"
    iso27001 = "iso27001"
    hipaa = "hipaa"
    internal = "internal"


@dataclass(frozen=True, slots=True)
class AuditExportRequest:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    requested_by: str = ""
    format: ExportFormat = ExportFormat.json
    date_from: datetime | None = None
    date_to: datetime | None = None
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class DataRetentionPolicy:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    data_category: str = ""
    retention_days: int = 90
    archival_days: int = 365
    deletion_after_days: int = 730


@dataclass(frozen=True, slots=True)
class LegalHold:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    case_name: str = ""
    data_categories: tuple[str, ...] = ()
    applied_by: str = ""
    applied_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    released_at: datetime | None = None
    active: bool = True


@dataclass(frozen=True, slots=True)
class RegionalDataPolicy:
    id: UUID = field(default_factory=uuid4)
    region: str = ""
    data_categories: tuple[str, ...] = ()
    requires_local_storage: bool = True
    export_restricted: bool = False


@dataclass(frozen=True, slots=True)
class ComplianceReport:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    framework: ComplianceFramework = ComplianceFramework.internal
    status: str = "compliant"
    findings: tuple[str, ...] = ()
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
