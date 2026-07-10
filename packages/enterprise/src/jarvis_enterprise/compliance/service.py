"""Compliance center service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.compliance.models import (
    AuditExportRequest,
    ComplianceFramework,
    ComplianceReport,
    DataRetentionPolicy,
    ExportFormat,
    LegalHold,
    RegionalDataPolicy,
)


class ComplianceCenterService:
    def __init__(self) -> None:
        self._export_requests: dict[UUID, AuditExportRequest] = {}
        self._retention_policies: dict[UUID, DataRetentionPolicy] = {}
        self._legal_holds: dict[UUID, LegalHold] = {}
        self._regional_policies: dict[UUID, RegionalDataPolicy] = {}
        self._reports: dict[UUID, ComplianceReport] = {}

    def request_audit_export(
        self, org_id: UUID, requested_by: str,
        format: ExportFormat = ExportFormat.json,
    ) -> AuditExportRequest:
        req = AuditExportRequest(org_id=org_id, requested_by=requested_by, format=format)
        self._export_requests[req.id] = req
        return req

    def list_export_requests(self, org_id: UUID) -> list[AuditExportRequest]:
        return [r for r in self._export_requests.values() if r.org_id == org_id]

    def create_retention_policy(
        self, org_id: UUID, data_category: str,
        retention_days: int = 90, archival_days: int = 365,
    ) -> DataRetentionPolicy:
        policy = DataRetentionPolicy(
            org_id=org_id, data_category=data_category,
            retention_days=retention_days, archival_days=archival_days,
        )
        self._retention_policies[policy.id] = policy
        return policy

    def list_retention_policies(self, org_id: UUID) -> list[DataRetentionPolicy]:
        return [p for p in self._retention_policies.values() if p.org_id == org_id]

    def apply_legal_hold(self, org_id: UUID, case_name: str, data_categories: tuple[str, ...], applied_by: str) -> LegalHold:
        hold = LegalHold(org_id=org_id, case_name=case_name, data_categories=data_categories, applied_by=applied_by)
        self._legal_holds[hold.id] = hold
        return hold

    def release_legal_hold(self, hold_id: UUID) -> LegalHold | None:
        hold = self._legal_holds.get(hold_id)
        if hold is None:
            return None
        updated = LegalHold(
            id=hold.id, org_id=hold.org_id, case_name=hold.case_name,
            data_categories=hold.data_categories, applied_by=hold.applied_by,
            applied_at=hold.applied_at, released_at=datetime.now(timezone.utc),
            active=False,
        )
        self._legal_holds[hold_id] = updated
        return updated

    def list_legal_holds(self, org_id: UUID) -> list[LegalHold]:
        return [h for h in self._legal_holds.values() if h.org_id == org_id]

    def create_regional_policy(self, region: str, data_categories: tuple[str, ...]) -> RegionalDataPolicy:
        policy = RegionalDataPolicy(region=region, data_categories=data_categories)
        self._regional_policies[policy.id] = policy
        return policy

    def generate_compliance_report(self, org_id: UUID, framework: ComplianceFramework) -> ComplianceReport:
        report = ComplianceReport(org_id=org_id, framework=framework)
        self._reports[report.id] = report
        return report

    def list_compliance_reports(self, org_id: UUID) -> list[ComplianceReport]:
        return [r for r in self._reports.values() if r.org_id == org_id]
