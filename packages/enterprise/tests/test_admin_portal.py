"""Tests for Administration Portal."""

from uuid import uuid4

from jarvis_enterprise.admin_portal.models import (
    AdminDashboard,
    AuditEventType,
    AuditLogEntry,
    PlatformConfiguration,
)
from jarvis_enterprise.admin_portal.service import AdministrationPortalService


class TestAdminPortalService:
    def setup_method(self):
        self.repo = AdministrationPortalService()

    def test_log_event(self):
        entry = self.repo.log_event(uuid4(), AuditEventType.organization_created, "admin")
        assert entry.event_type == AuditEventType.organization_created

    def test_get_audit_log(self):
        org_id = uuid4()
        self.repo.log_event(org_id, AuditEventType.workspace_created, "admin")
        self.repo.log_event(org_id, AuditEventType.user_invited, "admin")
        assert len(self.repo.get_audit_log(org_id)) == 2

    def test_audit_log_isolation(self):
        org1, org2 = uuid4(), uuid4()
        self.repo.log_event(org1, AuditEventType.organization_created, "admin")
        self.repo.log_event(org2, AuditEventType.organization_created, "admin")
        assert len(self.repo.get_audit_log(org1)) == 1

    def test_set_configuration(self):
        config = self.repo.set_configuration("max_workspaces", "50", "limits", "admin", "Max workspaces per org")
        assert config.key == "max_workspaces"
        assert config.value == "50"

    def test_get_configuration(self):
        self.repo.set_configuration("feature_x", True, "features")
        config = self.repo.get_configuration("feature_x")
        assert config is not None
        assert config.value is True

    def test_list_configurations_by_category(self):
        self.repo.set_configuration("k1", "v1", "cat1")
        self.repo.set_configuration("k2", "v2", "cat2")
        self.repo.set_configuration("k3", "v3", "cat1")
        assert len(self.repo.list_configurations("cat1")) == 2

    def test_dashboard(self):
        dashboard = self.repo.get_dashboard(org_count=3, ws_count=15, user_count=200)
        assert dashboard.total_organizations == 3
        assert dashboard.total_workspaces == 15
        assert dashboard.total_users == 200
