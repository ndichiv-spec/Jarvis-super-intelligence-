from __future__ import annotations

from datetime import UTC, datetime

import pytest
from jarvis_security.audit import AuditEvent, AuditEventType, AuditField, InMemoryAuditSink
from jarvis_security.authorization import AuthorizationRequest
from jarvis_security.context import ExecutionContextType
from jarvis_security.identity import Identity, IdentityType
from jarvis_security.kernel import SecurityKernel
from jarvis_security.organization import OrganizationModel, OrganizationUnit, OrganizationUnitType
from jarvis_security.policy import (
    ComparisonOperator,
    PolicyAttribute,
    PolicyCondition,
    PolicyEffect,
    PolicyEngine,
    PolicyEvaluationRequest,
    PolicyRule,
    PolicyType,
)
from jarvis_security.roles import Capability, RoleCatalog, RoleDefinition
from jarvis_security.workspace import WorkspaceBoundary, WorkspaceIsolationManager


def _make_user(identity_id: str = "user-1") -> Identity:
    return Identity.create(
        identity_type=IdentityType.USER,
        identifier=identity_id,
        owner_identifier=identity_id,
        display_name="Primary User",
        workspace_identifier="ws-1",
        organization_identifier="org-1",
    )


class TestIdentityCreation:
    def test_identity_creation_contains_immutable_metadata(self) -> None:
        user = _make_user("user-abc")

        assert user.immutable_id == "user-abc"
        assert user.metadata.identifier == "user-abc"
        assert user.metadata.workspace_identifier == "ws-1"
        assert user.metadata.organization_identifier == "org-1"
        assert user.identity_type is IdentityType.USER

    def test_identity_creation_rejects_type_metadata_mismatch(self) -> None:
        with pytest.raises(ValueError):
            Identity.create(
                identity_type=IdentityType.AGENT,
                identifier="agent-1",
                owner_identifier="agent-1",
                display_name="",
            )


class TestRoleAndPermissionEvaluation:
    def test_predefined_role_permission_resolution(self) -> None:
        catalog = RoleCatalog()

        permissions = catalog.resolve_permissions(("developer",))

        assert "tools:execute:*" in permissions
        assert "projects:manage:*" in permissions

    def test_custom_role_inheritance_resolves_permissions(self) -> None:
        catalog = RoleCatalog()
        custom = RoleDefinition.create(
            name="custom_research_admin",
            description="Composed role",
            permissions=("knowledge:write:*",),
            capabilities=(Capability(namespace="analysis", action="review", resource="*"),),
            inherited_roles=("researcher",),
            owner_identifier="system",
        )
        catalog.register(custom)

        permissions = set(catalog.resolve_permissions(("custom_research_admin",)))
        capabilities = {
            item.key
            for item in catalog.resolve_capabilities(("custom_research_admin",))
        }

        assert "knowledge:write:*" in permissions
        assert "knowledge:read:*" in permissions
        assert "analysis:review:*" in capabilities


class TestPolicyEngine:
    def test_deny_policy_takes_precedence(self) -> None:
        engine = PolicyEngine()
        engine.register_rule(
            PolicyRule.create(
                name="allow_tools",
                policy_type=PolicyType.RESOURCE,
                effect=PolicyEffect.ALLOW,
                owner_identifier="system",
                action_pattern="tools.execute",
                resource_pattern="tool:*",
                priority=1,
            ),
        )
        engine.register_rule(
            PolicyRule.create(
                name="deny_sensitive_tools",
                policy_type=PolicyType.RESOURCE,
                effect=PolicyEffect.DENY,
                owner_identifier="system",
                action_pattern="tools.execute",
                resource_pattern="tool:sensitive-*",
                priority=10,
            ),
        )

        decision = engine.evaluate(
            PolicyEvaluationRequest(
                actor_identifier="user-1",
                actor_identity_type=IdentityType.USER,
                actor_roles=("developer",),
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                action="tools.execute",
                resource="tool:sensitive-network",
            ),
        )

        assert not decision.allowed
        assert decision.effect is PolicyEffect.DENY

    def test_conditional_policy_evaluates_attributes(self) -> None:
        engine = PolicyEngine()
        engine.register_rule(
            PolicyRule.create(
                name="allow_high_trust_extensions",
                policy_type=PolicyType.EXTENSION,
                effect=PolicyEffect.CONDITIONAL,
                owner_identifier="system",
                action_pattern="extension.load",
                resource_pattern="ext:*",
                conditions=(
                    PolicyCondition(
                        attribute="trust_level",
                        operator=ComparisonOperator.EQUALS,
                        expected="4",
                    ),
                ),
                priority=5,
            ),
        )

        decision = engine.evaluate(
            PolicyEvaluationRequest(
                actor_identifier="user-1",
                actor_identity_type=IdentityType.USER,
                actor_roles=("extension_publisher",),
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                action="extension.load",
                resource="ext:trusted-ai",
                attributes=(PolicyAttribute(key="trust_level", value="4"),),
            ),
        )

        assert decision.allowed
        assert decision.effect is PolicyEffect.CONDITIONAL


class TestWorkspaceIsolation:
    def test_workspace_membership_controls_access(self) -> None:
        isolation = WorkspaceIsolationManager()
        isolation.register_boundary(
            WorkspaceBoundary.create(
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                owner_identifier="owner-1",
                isolation_key="isolation-a",
            ),
        )
        isolation.register_boundary(
            WorkspaceBoundary.create(
                workspace_identifier="ws-2",
                organization_identifier="org-1",
                owner_identifier="owner-1",
                isolation_key="isolation-b",
            ),
        )
        isolation.add_membership(
            identity_identifier="user-1",
            workspace_identifier="ws-1",
            organization_identifier="org-1",
            role_names=("developer",),
            owner_identifier="owner-1",
        )

        assert isolation.can_access_identity(
            identity_identifier="user-1",
            workspace_identifier="ws-1",
            organization_identifier="org-1",
        )
        assert not isolation.can_access_identity(
            identity_identifier="user-1",
            workspace_identifier="ws-2",
            organization_identifier="org-1",
        )
        assert isolation.assert_isolated("ws-1", "ws-1")
        assert not isolation.assert_isolated("ws-1", "ws-2")


class TestOrganizationHierarchy:
    def test_hierarchy_and_membership_resolution(self) -> None:
        model = OrganizationModel()
        root = OrganizationUnit.create(
            identifier="org-1",
            owner_identifier="owner-1",
            name="Acme",
            unit_type=OrganizationUnitType.ORGANIZATION,
        )
        department = OrganizationUnit.create(
            identifier="dep-1",
            owner_identifier="owner-1",
            name="Research",
            unit_type=OrganizationUnitType.DEPARTMENT,
            parent_identifier="org-1",
        )
        team = OrganizationUnit.create(
            identifier="team-1",
            owner_identifier="owner-1",
            name="AI Team",
            unit_type=OrganizationUnitType.TEAM,
            parent_identifier="dep-1",
        )
        model.register_unit(root)
        model.register_unit(department)
        model.register_unit(team)
        model.add_membership(
            identity_identifier="user-1",
            unit_identifier="team-1",
            role_name="developer",
            owner_identifier="owner-1",
        )

        lineage = model.lineage("team-1")

        assert tuple(unit.metadata.identifier for unit in lineage) == ("team-1", "dep-1", "org-1")
        assert model.is_member("user-1", "team-1")
        assert model.is_member("user-1", "org-1")


class TestAuditContracts:
    def test_audit_event_generation_and_filtering(self) -> None:
        sink = InMemoryAuditSink()
        auth_event = AuditEvent.create(
            event_type=AuditEventType.AUTHENTICATION,
            actor_identifier="user-1",
            owner_identifier="user-1",
            summary="Login accepted",
            details=(AuditField(key="method", value="passkey"),),
        )
        authz_event = AuditEvent.create(
            event_type=AuditEventType.AUTHORIZATION,
            actor_identifier="user-1",
            owner_identifier="user-1",
            summary="Tool execution allowed",
        )
        sink.record(auth_event)
        sink.record(authz_event)

        assert len(sink.list_events()) == 2
        assert len(sink.list_events(AuditEventType.AUTHENTICATION)) == 1


class TestSecurityKernelBehavior:
    def test_kernel_authorization_success_and_audit(self) -> None:
        kernel = SecurityKernel()
        user = _make_user("owner-1")
        kernel.register_identity(user)
        kernel.register_organization_unit(
            OrganizationUnit.create(
                identifier="org-1",
                owner_identifier="owner-1",
                name="Acme",
                unit_type=OrganizationUnitType.ORGANIZATION,
            ),
        )
        kernel.register_workspace(
            WorkspaceBoundary.create(
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                owner_identifier="owner-1",
                isolation_key="isolation-1",
            ),
        )
        kernel.workspace_isolation.add_membership(
            identity_identifier="owner-1",
            workspace_identifier="ws-1",
            organization_identifier="org-1",
            role_names=("owner",),
            owner_identifier="owner-1",
        )

        context = kernel.issue_context(
            identity_identifier="owner-1",
            role_names=("owner",),
            workspace_identifier="ws-1",
            organization_identifier="org-1",
            execution_context=ExecutionContextType.INTERACTIVE,
            session_identifier="session-1",
        )

        decision = kernel.authorize(
            AuthorizationRequest(
                security_context=context,
                action="tools.execute",
                resource="tool:workspace-inspect",
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                required_permissions=("tools:execute:*",),
            ),
        )

        assert decision.allowed
        assert not decision.missing_permissions
        assert len(kernel.list_audit_events(AuditEventType.AUTHORIZATION)) == 1
        assert len(kernel.list_audit_events(AuditEventType.POLICY_DECISION)) == 1

    def test_kernel_authorization_denied_by_policy(self) -> None:
        kernel = SecurityKernel()
        user = _make_user("user-2")
        kernel.register_identity(user)
        kernel.register_organization_unit(
            OrganizationUnit.create(
                identifier="org-1",
                owner_identifier="owner-1",
                name="Acme",
                unit_type=OrganizationUnitType.ORGANIZATION,
            ),
        )
        kernel.register_workspace(
            WorkspaceBoundary.create(
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                owner_identifier="owner-1",
                isolation_key="isolation-1",
            ),
        )
        kernel.workspace_isolation.add_membership(
            identity_identifier="user-2",
            workspace_identifier="ws-1",
            organization_identifier="org-1",
            role_names=("developer",),
            owner_identifier="owner-1",
        )
        kernel.register_policy(
            PolicyRule.create(
                name="deny_tool",
                policy_type=PolicyType.RESOURCE,
                effect=PolicyEffect.DENY,
                owner_identifier="owner-1",
                action_pattern="tools.execute",
                resource_pattern="tool:blocked-*",
                priority=100,
            ),
        )

        context = kernel.issue_context(
            identity_identifier="user-2",
            role_names=("developer",),
            workspace_identifier="ws-1",
            organization_identifier="org-1",
            execution_context=ExecutionContextType.INTERACTIVE,
            session_identifier="session-2",
        )

        decision = kernel.authorize(
            AuthorizationRequest(
                security_context=context,
                action="tools.execute",
                resource="tool:blocked-network",
                workspace_identifier="ws-1",
                organization_identifier="org-1",
                required_permissions=("tools:execute:*",),
            ),
        )

        assert not decision.allowed
        assert "Denied by policy" in decision.reason


def test_metadata_timestamps_are_timezone_aware() -> None:
    user = _make_user("tz-user")

    assert user.metadata.created_timestamp.tzinfo is UTC
    assert user.metadata.updated_timestamp.tzinfo is UTC
    assert user.metadata.updated_timestamp >= user.metadata.created_timestamp
    assert datetime.now(tz=UTC) >= user.metadata.created_timestamp
