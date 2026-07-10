"""Tests for Enterprise Security Center."""

from uuid import uuid4

from jarvis_enterprise.security_center.models import (
    IncidentReport,
    IncidentSeverity,
    IncidentStatus,
    RiskLevel,
    RiskReport,
    SecurityDashboard,
    SecurityPolicy,
)
from jarvis_enterprise.security_center.service import SecurityCenterService


class TestSecurityCenterService:
    def setup_method(self):
        self.repo = SecurityCenterService()

    def test_create_security_policy(self):
        policy = self.repo.create_security_policy(uuid4(), "MFA Required")
        assert policy.name == "MFA Required"

    def test_report_incident(self):
        org_id = uuid4()
        incident = self.repo.report_incident(org_id, "Data Breach", "Sensitive data exposed", IncidentSeverity.critical)
        assert incident.severity == IncidentSeverity.critical
        assert incident.status == IncidentStatus.open

    def test_resolve_incident(self):
        org_id = uuid4()
        incident = self.repo.report_incident(org_id, "Issue", "desc")
        resolved = self.repo.resolve_incident(incident.id, "Fixed")
        assert resolved is not None
        assert resolved.status == IncidentStatus.resolved

    def test_list_incidents(self):
        org_id = uuid4()
        self.repo.report_incident(org_id, "Incident 1", "desc")
        self.repo.report_incident(org_id, "Incident 2", "desc")
        assert len(self.repo.list_incidents(org_id)) == 2

    def test_list_incidents_isolation(self):
        org1, org2 = uuid4(), uuid4()
        self.repo.report_incident(org1, "Org1 Issue", "desc")
        self.repo.report_incident(org2, "Org2 Issue", "desc")
        assert len(self.repo.list_incidents(org1)) == 1

    def test_create_risk_report(self):
        org_id = uuid4()
        risk = self.repo.create_risk_report(org_id, "Data Loss Risk", "Risk of data loss", RiskLevel.high)
        assert risk.risk_level == RiskLevel.high

    def test_dashboard(self):
        org_id = uuid4()
        self.repo.report_incident(org_id, "Critical Issue", "desc", IncidentSeverity.critical)
        self.repo.report_incident(org_id, "Minor Issue", "desc", IncidentSeverity.low)
        dashboard = self.repo.get_dashboard(org_id)
        assert dashboard.total_incidents == 2
        assert dashboard.critical_incidents == 1
