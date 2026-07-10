from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from jarvis_security.audit import AuditEvent, AuditEventType, AuditField, InMemoryAuditSink
from jarvis_security.authorization import (
    AuthorizationDecision,
    AuthorizationEngine,
    AuthorizationRequest,
)
from jarvis_security.context import ExecutionContextType, SecurityContext, SessionContext
from jarvis_security.identity import Identity, InMemoryIdentityRegistry
from jarvis_security.metadata import SecurityObjectType, new_metadata
from jarvis_security.organization import OrganizationModel, OrganizationUnit
from jarvis_security.permissions import Permission, PermissionCatalog
from jarvis_security.policy import (
    PolicyDecision,
    PolicyEngine,
    PolicyEvaluationRequest,
    PolicyRule,
)
from jarvis_security.roles import RoleCatalog, RoleDefinition
from jarvis_security.trust import TrustLevel, TrustModel
from jarvis_security.workspace import WorkspaceBoundary, WorkspaceIsolationManager


@dataclass(slots=True)
class SecurityKernel:
    identity_registry: InMemoryIdentityRegistry = field(default_factory=InMemoryIdentityRegistry)
    role_catalog: RoleCatalog = field(default_factory=RoleCatalog)
    permission_catalog: PermissionCatalog = field(default_factory=PermissionCatalog)
    policy_engine: PolicyEngine = field(default_factory=PolicyEngine)
    workspace_isolation: WorkspaceIsolationManager = field(
        default_factory=WorkspaceIsolationManager,
    )
    organization_model: OrganizationModel = field(default_factory=OrganizationModel)
    trust_model: TrustModel = field(default_factory=TrustModel)
    audit_sink: InMemoryAuditSink = field(default_factory=InMemoryAuditSink)
    authorization_engine: AuthorizationEngine = field(init=False)

    def __post_init__(self) -> None:
        self.authorization_engine = AuthorizationEngine(
            role_catalog=self.role_catalog,
            policy_engine=self.policy_engine,
            workspace_isolation=self.workspace_isolation,
            organization_model=self.organization_model,
        )

    def register_identity(self, identity: Identity) -> Identity:
        registered = self.identity_registry.register(identity)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=identity.metadata.owner_identifier,
            target_identifier=identity.immutable_id,
            summary=f"Registered identity {identity.immutable_id}",
            workspace_identifier=identity.metadata.workspace_identifier,
            organization_identifier=identity.metadata.organization_identifier,
        )
        return registered

    def register_role(self, role: RoleDefinition) -> RoleDefinition:
        registered = self.role_catalog.register(role)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=role.metadata.owner_identifier,
            target_identifier=role.metadata.identifier,
            summary=f"Registered role {role.name}",
        )
        return registered

    def register_permission(self, permission: Permission) -> Permission:
        registered = self.permission_catalog.register(permission)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=permission.metadata.owner_identifier,
            target_identifier=permission.metadata.identifier,
            summary=f"Registered permission {permission.key}",
        )
        return registered

    def register_policy(self, rule: PolicyRule) -> PolicyRule:
        registered = self.policy_engine.register_rule(rule)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=rule.metadata.owner_identifier,
            target_identifier=rule.metadata.identifier,
            summary=f"Registered policy {rule.name}",
        )
        return registered

    def register_workspace(self, boundary: WorkspaceBoundary) -> WorkspaceBoundary:
        registered = self.workspace_isolation.register_boundary(boundary)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=boundary.metadata.owner_identifier,
            target_identifier=boundary.metadata.identifier,
            summary=f"Registered workspace boundary {boundary.workspace_identifier}",
            workspace_identifier=boundary.workspace_identifier,
            organization_identifier=boundary.organization_identifier,
        )
        return registered

    def register_organization_unit(self, unit: OrganizationUnit) -> OrganizationUnit:
        registered = self.organization_model.register_unit(unit)
        self._record_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor_identifier=unit.metadata.owner_identifier,
            target_identifier=unit.metadata.identifier,
            summary=f"Registered organization unit {unit.name}",
            organization_identifier=unit.metadata.organization_identifier,
        )
        return registered

    def issue_context(
        self,
        *,
        identity_identifier: str,
        role_names: tuple[str, ...],
        workspace_identifier: str,
        organization_identifier: str,
        execution_context: ExecutionContextType,
        session_identifier: str | None = None,
        explicit_permissions: tuple[str, ...] = (),
        trust_target_identifier: str | None = None,
    ) -> SecurityContext:
        identity = self.identity_registry.get(identity_identifier)
        if identity is None:
            raise KeyError(f"Unknown identity: {identity_identifier}")

        role_permissions = self.role_catalog.resolve_permissions(role_names)
        capabilities = self.role_catalog.resolve_capabilities(role_names)
        permission_keys = tuple(sorted(set(role_permissions).union(explicit_permissions)))

        inherited_workspaces = tuple(
            membership.workspace_identifier
            for membership in self.workspace_isolation.list_memberships(identity_identifier)
        )
        inherited_organizations = tuple(
            membership.unit_identifier
            for membership in self.organization_model.list_memberships(identity_identifier)
        )

        workspace_memberships = tuple(
            sorted(
                {
                    workspace_identifier,
                    *inherited_workspaces,
                },
            ),
        )
        organization_memberships = tuple(
            sorted(
                {
                    organization_identifier,
                    *inherited_organizations,
                },
            ),
        )

        trust_level = (
            self.trust_model.evaluate(identity_identifier, trust_target_identifier)
            if trust_target_identifier is not None
            else TrustLevel.MEDIUM
        )

        issued_at = datetime.now(tz=UTC)
        session = (
            SessionContext.create(
                session_identifier=session_identifier,
                owner_identifier=identity_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
                issued_at=issued_at,
                expires_at=issued_at + timedelta(hours=8),
            )
            if session_identifier is not None
            else None
        )

        context = SecurityContext(
            metadata=new_metadata(
                object_type=SecurityObjectType.SECURITY_CONTEXT,
                owner_identifier=identity_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            identity=identity,
            role_names=role_names,
            permission_keys=permission_keys,
            capabilities=capabilities,
            workspace_identifier=workspace_identifier,
            organization_identifier=organization_identifier,
            workspace_memberships=workspace_memberships,
            organization_memberships=organization_memberships,
            session=session,
            execution_context=execution_context,
            trust_level=trust_level,
        )

        self._record_event(
            event_type=AuditEventType.AUTHENTICATION,
            actor_identifier=identity_identifier,
            target_identifier=session_identifier,
            summary="Issued security context",
            workspace_identifier=workspace_identifier,
            organization_identifier=organization_identifier,
            details=(
                AuditField(key="roles", value=",".join(role_names)),
                AuditField(key="trust_level", value=str(int(trust_level))),
            ),
        )
        return context

    def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = self.authorization_engine.authorize(request)
        self._record_event(
            event_type=AuditEventType.AUTHORIZATION,
            actor_identifier=request.security_context.identity.immutable_id,
            target_identifier=request.resource,
            summary="Authorization evaluated",
            workspace_identifier=request.workspace_identifier,
            organization_identifier=request.organization_identifier,
            details=(
                AuditField(key="allowed", value=str(decision.allowed)),
                AuditField(key="reason", value=decision.reason),
            ),
        )
        self._record_event(
            event_type=AuditEventType.POLICY_DECISION,
            actor_identifier=request.security_context.identity.immutable_id,
            target_identifier=request.resource,
            summary=decision.policy_decision.reason,
            workspace_identifier=request.workspace_identifier,
            organization_identifier=request.organization_identifier,
            details=(
                AuditField(
                    key="matched_rules",
                    value=",".join(decision.policy_decision.matched_rule_identifiers),
                ),
            ),
        )
        return decision

    def evaluate_policy(self, request: PolicyEvaluationRequest) -> PolicyDecision:
        decision = self.policy_engine.evaluate(request)
        self._record_event(
            event_type=AuditEventType.POLICY_DECISION,
            actor_identifier=request.actor_identifier,
            target_identifier=request.resource,
            summary=decision.reason,
            workspace_identifier=request.workspace_identifier,
            organization_identifier=request.organization_identifier,
        )
        return decision

    def list_audit_events(self, event_type: AuditEventType | None = None) -> tuple[AuditEvent, ...]:
        return self.audit_sink.list_events(event_type=event_type)

    def _record_event(
        self,
        *,
        event_type: AuditEventType,
        actor_identifier: str,
        summary: str,
        target_identifier: str | None = None,
        details: tuple[AuditField, ...] = (),
        workspace_identifier: str | None = None,
        organization_identifier: str | None = None,
    ) -> None:
        self.audit_sink.record(
            AuditEvent.create(
                event_type=event_type,
                actor_identifier=actor_identifier,
                owner_identifier=actor_identifier,
                summary=summary,
                target_identifier=target_identifier,
                details=details,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
        )
