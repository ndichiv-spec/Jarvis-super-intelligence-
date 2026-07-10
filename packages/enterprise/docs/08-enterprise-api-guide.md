# Enterprise Platform API Guide

## Platform Kernel

### `EnterprisePlatform`
Central orchestrator composing all enterprise domain services.

**Constructor Parameters:**
- `organization_service: OrganizationService`
- `workspace_service: WorkspaceAdministrationService`
- `user_service: UserAdministrationService`
- `governance_service: EnterpriseGovernanceService`
- `collaboration_service: CollaborationService`
- `security_service: SecurityCenterService`
- `observability_service: EnterpriseObservabilityService`
- `resource_service: ResourceManagementService`
- `billing_service: BillingPreparationService`
- `compliance_service: ComplianceCenterService`
- `integration_service: IntegrationHubService`
- `admin_service: AdministrationPortalService`
- `analytics_service: AnalyticsService`
- `continuity_service: BusinessContinuityService`

**Methods:**
- `initialize() -> EnterprisePlatformState` — Set platform to ready
- `health() -> dict` — Returns current health summary

---

## Organization Service

### `OrganizationService(repository: OrganizationRepository)`
- `create_organization(name, display_name, description) -> Organization`
- `get_organization(org_id) -> Organization | None`
- `suspend_organization(org_id) -> Organization | None`
- `archive_organization(org_id) -> Organization | None`
- `list_organizations() -> list[Organization]`
- `add_unit(org_id, name, unit_type, parent_id) -> OrgUnit | None`
- `add_member(org_id, user_id, role) -> OrganizationMember | None`
- `remove_member(org_id, user_id) -> bool`
- `get_members(org_id) -> list[OrganizationMember]`

---

## Workspace Service

### `WorkspaceAdministrationService(repository: WorkspaceRepository)`
- `create_workspace(org_id, name, owner_id, ...) -> Workspace`
- `get_workspace(workspace_id) -> Workspace | None`
- `suspend_workspace(workspace_id) -> Workspace | None`
- `list_workspaces(org_id) -> list[Workspace]`
- `add_member(workspace_id, user_id, role) -> WorkspaceMembership | None`
- `remove_member(workspace_id, user_id) -> bool`
- `get_members(workspace_id) -> list[WorkspaceMembership]`
- `create_project(workspace_id, name, owner_id, ...) -> Project | None`
- `list_projects(workspace_id) -> list[Project]`
- `set_resource_allocation(workspace_id, resource_type, limit) -> ResourceAllocation | None`
- `get_resource_allocation(workspace_id, resource_type) -> ResourceAllocation | None`

---

## User Service

### `UserAdministrationService(repository: EnterpriseUserRepository)`
- `create_user(user_id, email, display_name) -> EnterpriseUser`
- `get_user(user_id) -> EnterpriseUser | None`
- `suspend_user(user_id) -> EnterpriseUser | None`
- `list_users(org_id) -> list[EnterpriseUser]`
- `assign_user_to_org(user_id, org_id) -> EnterpriseUser | None`
- `invite_user(email, org_id, invited_by, role) -> Invitation`
- `accept_invitation(invitation_id) -> Invitation | None`
- `create_access_review(org_id, reviewer_id, target_user_id) -> AccessReview`

---

## Governance Service

### `EnterpriseGovernanceService(repository: GovernanceRepository)`
- `create_policy(name, description, scope, policy_type, rules) -> GovernancePolicy`
- `get_policy(policy_id) -> GovernancePolicy | None`
- `list_policies(scope) -> list[GovernancePolicy]`
- `enable_policy(policy_id) -> GovernancePolicy | None`
- `disable_policy(policy_id) -> GovernancePolicy | None`
- `create_data_rule(data_type, classification, retention_days) -> DataGovernanceRule`
- `create_retention_policy(name, data_category, retention_days) -> RetentionPolicy`
- `create_compliance_control(framework, control_id, description) -> ComplianceControl`
- `evaluate_policies(action, resource, scope_id) -> list[GovernancePolicy]`

---

## Other Services

### `CollaborationService` — Shared projects, discussions, review workflows, approvals
### `SecurityCenterService` — Security policies, incidents, risk reports, dashboards
### `EnterpriseObservabilityService` — Service health, usage metrics, availability, trends
### `ResourceManagementService` — Quotas, compute/storage allocation, usage policies
### `BillingPreparationService` — Plans, subscriptions, licenses, usage tracking, cost reports
### `ComplianceCenterService` — Audit exports, retention, legal hold, regional policies
### `IntegrationHubService` — Providers, adapters, capabilities
### `AdministrationPortalService` — Audit log, configuration, dashboards
### `AnalyticsService` — Reports, metrics, widgets
### `BusinessContinuityService` — Runbooks, incident plans, recovery procedures, backup validation

All services follow the same pattern: constructor injection of repository protocol, immutable domain models, and clear method signatures with optional parameters.

## Repository Protocols

All repository interfaces are defined as `Protocol` classes and support in-memory (for testing) or production implementations:

- `OrganizationRepository`
- `WorkspaceRepository`
- `EnterpriseUserRepository`
- `GovernanceRepository`
- `CollaborationRepository`
- `ResourceRepository`
- `BillingRepository`
- `IntegrationRepository`
- `AnalyticsRepository`
