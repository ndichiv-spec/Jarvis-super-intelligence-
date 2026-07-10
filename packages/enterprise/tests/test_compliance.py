"""Tests for Compliance Center."""

from uuid import uuid4

from jarvis_enterprise.compliance.models import (
    AuditExportRequest,
    ComplianceFramework,
    ComplianceReport,
    DataRetentionPolicy,
    ExportFormat,
    LegalHold,
    RegionalDataPolicy,
)
from jarvis_enterprise.compliance.service import ComplianceCenterService


class TestComplianceService:
    def setup_method(self):
        self.repo = ComplianceCenterService()

    def test_request_audit_export(self):
        req = self.repo.request_audit_export(uuid4(), "admin")
        assert req.status == "pending"

    def test_list_export_requests(self):
        org_id = uuid4()
        self.repo.request_audit_export(org_id, "admin")
        self.repo.request_audit_export(org_id, "admin")
        assert len(self.repo.list_export_requests(org_id)) == 2

    def test_create_retention_policy(self):
        policy = self.repo.create_retention_policy(uuid4(), "logs", 30, 180)
        assert policy.retention_days == 30
        assert policy.archival_days == 180

    def test_apply_legal_hold(self):
        hold = self.repo.apply_legal_hold(uuid4(), "Case #123", ("logs", "emails"), "admin")
        assert hold.case_name == "Case #123"
        assert hold.active is True

    def test_release_legal_hold(self):
        hold = self.repo.apply_legal_hold(uuid4(), "Case #123", ("logs",), "admin")
        released = self.repo.release_legal_hold(hold.id)
        assert released is not None
        assert released.active is False

    def test_create_regional_policy(self):
        policy = self.repo.create_regional_policy("EU", ("personal_data", "financial_data"))
        assert policy.region == "EU"
        assert policy.requires_local_storage is True

    def test_generate_compliance_report(self):
        report = self.repo.generate_compliance_report(uuid4(), ComplianceFramework.soc2)
        assert report.framework == ComplianceFramework.soc2
        assert report.status == "compliant"

    def test_legal_hold_isolation(self):
        org1, org2 = uuid4(), uuid4()
        self.repo.apply_legal_hold(org1, "Case A", ("data",), "admin")
        self.repo.apply_legal_hold(org2, "Case B", ("data",), "admin")
        assert len(self.repo.list_legal_holds(org1)) == 1
