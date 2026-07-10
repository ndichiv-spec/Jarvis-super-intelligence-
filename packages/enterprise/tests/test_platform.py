"""Tests for Enterprise Platform Kernel."""

from uuid import uuid4

from jarvis_enterprise.platform.kernel import EnterprisePlatform, EnterprisePlatformStatus
from jarvis_enterprise.organization.service import OrganizationService
from jarvis_enterprise.workspace.service import WorkspaceAdministrationService
from jarvis_enterprise.user.service import UserAdministrationService
from jarvis_enterprise.governance.service import EnterpriseGovernanceService
from jarvis_enterprise.collaboration.service import CollaborationService
from jarvis_enterprise.security_center.service import SecurityCenterService
from jarvis_enterprise.observability.service import EnterpriseObservabilityService
from jarvis_enterprise.resource_management.service import ResourceManagementService
from jarvis_enterprise.billing.service import BillingPreparationService
from jarvis_enterprise.compliance.service import ComplianceCenterService
from jarvis_enterprise.integration.service import IntegrationHubService
from jarvis_enterprise.admin_portal.service import AdministrationPortalService
from jarvis_enterprise.analytics.service import AnalyticsService
from jarvis_enterprise.continuity.service import BusinessContinuityService

from tests.test_organization import InMemoryOrgRepository
from tests.test_workspace import InMemoryWorkspaceRepository
from tests.test_user import InMemoryUserRepository
from tests.test_governance import InMemoryGovernanceRepo
from tests.test_collaboration import InMemoryCollabRepo
from tests.test_resource_management import InMemoryResourceRepo
from tests.test_billing import InMemoryBillingRepo
from tests.test_integration import InMemoryIntegrationRepo
from tests.test_analytics import InMemoryAnalyticsRepo


class TestEnterprisePlatform:
    def setup_method(self):
        self.platform = EnterprisePlatform(
            organization_service=OrganizationService(InMemoryOrgRepository()),
            workspace_service=WorkspaceAdministrationService(InMemoryWorkspaceRepository()),
            user_service=UserAdministrationService(InMemoryUserRepository()),
            governance_service=EnterpriseGovernanceService(InMemoryGovernanceRepo()),
            collaboration_service=CollaborationService(InMemoryCollabRepo()),
            security_service=SecurityCenterService(),
            observability_service=EnterpriseObservabilityService(),
            resource_service=ResourceManagementService(InMemoryResourceRepo()),
            billing_service=BillingPreparationService(InMemoryBillingRepo()),
            compliance_service=ComplianceCenterService(),
            integration_service=IntegrationHubService(InMemoryIntegrationRepo()),
            admin_service=AdministrationPortalService(),
            analytics_service=AnalyticsService(InMemoryAnalyticsRepo()),
            continuity_service=BusinessContinuityService(),
        )

    def test_initial_state(self):
        assert self.platform.state.status == EnterprisePlatformStatus.ready

    def test_initialize(self):
        state = self.platform.initialize()
        assert state.status == EnterprisePlatformStatus.ready
        assert state.initialized_at is not None

    def test_health(self):
        health = self.platform.health()
        assert health["platform"] == "ready"

    def test_organization_service_accessible(self):
        org = self.platform.organizations.create_organization("Enterprise Corp")
        assert org.name == "Enterprise Corp"

    def test_workspace_service_accessible(self):
        org_id = uuid4()
        ws = self.platform.workspaces.create_workspace(org_id, "dev", "owner1")
        assert ws.name == "dev"

    def test_user_service_accessible(self):
        user = self.platform.users.create_user("u1", "user@test.com")
        assert user.id == "u1"

    def test_governance_service_accessible(self):
        from jarvis_enterprise.governance.models import PolicyScope
        policy = self.platform.governance.create_policy("Retention", "90 day retention", PolicyScope.global_)
        assert policy.name == "Retention"

    def test_collaboration_service_accessible(self):
        project = self.platform.collaboration.create_shared_project(uuid4(), "Enterprise Project", "owner1")
        assert project.name == "Enterprise Project"

    def test_security_service_accessible(self):
        incident = self.platform.security.report_incident(uuid4(), "Test Incident", "desc")
        assert incident.title == "Test Incident"

    def test_observability_service_accessible(self):
        from jarvis_enterprise.observability.models import ServiceStatus
        self.platform.observability.report_service_health("api", ServiceStatus.healthy)
        health = self.platform.observability.get_platform_health(uuid4())
        assert health.total_services == 1

    def test_billing_service_accessible(self):
        from jarvis_enterprise.billing.models import SubscriptionTier
        plan = self.platform.billing.create_plan("Enterprise", SubscriptionTier.enterprise, 100, 50, 1000)
        assert plan.tier == SubscriptionTier.enterprise

    def test_compliance_service_accessible(self):
        req = self.platform.compliance.request_audit_export(uuid4(), "auditor")
        assert req.status == "pending"

    def test_integration_service_accessible(self):
        from jarvis_enterprise.integration.models import IntegrationProviderKind
        provider = self.platform.integration.register_provider("Slack", IntegrationProviderKind.collaboration)
        assert provider.name == "Slack"

    def test_admin_portal_accessible(self):
        from jarvis_enterprise.admin_portal.models import AuditEventType
        entry = self.platform.admin.log_event(uuid4(), AuditEventType.organization_created, "admin")
        assert entry.actor_id == "admin"

    def test_analytics_service_accessible(self):
        from jarvis_enterprise.analytics.models import ReportCategory
        definition = self.platform.analytics.create_report_definition("Monthly Usage", ReportCategory.usage)
        assert definition.name == "Monthly Usage"

    def test_continuity_service_accessible(self):
        runbook = self.platform.continuity.create_runbook("Disaster Recovery", description="Full DR plan")
        assert runbook.description == "Full DR plan"
