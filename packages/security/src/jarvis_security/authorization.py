from __future__ import annotations

from dataclasses import dataclass

from jarvis_security.context import SecurityContext
from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata
from jarvis_security.organization import OrganizationModel
from jarvis_security.policy import (
    PolicyAttribute,
    PolicyDecision,
    PolicyEngine,
    PolicyEvaluationRequest,
)
from jarvis_security.roles import Capability, RoleCatalog
from jarvis_security.workspace import WorkspaceIsolationManager


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    security_context: SecurityContext
    action: str
    resource: str
    workspace_identifier: str
    organization_identifier: str
    owner_identifier: str | None = None
    required_permissions: tuple[str, ...] = ()
    required_capabilities: tuple[Capability, ...] = ()
    attributes: tuple[PolicyAttribute, ...] = ()

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action cannot be empty")
        if not self.resource.strip():
            raise ValueError("resource cannot be empty")
        if not self.workspace_identifier.strip():
            raise ValueError("workspace_identifier cannot be empty")
        if not self.organization_identifier.strip():
            raise ValueError("organization_identifier cannot be empty")


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    metadata: SecurityMetadata
    allowed: bool
    reason: str
    missing_permissions: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    policy_decision: PolicyDecision
    ownership_granted: bool = False


@dataclass(slots=True)
class AuthorizationEngine:
    role_catalog: RoleCatalog
    policy_engine: PolicyEngine
    workspace_isolation: WorkspaceIsolationManager
    organization_model: OrganizationModel

    def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        context = request.security_context
        has_workspace_access = self.workspace_isolation.can_access_context(
            workspace_memberships=context.workspace_memberships,
            organization_memberships=context.organization_memberships,
            workspace_identifier=request.workspace_identifier,
            organization_identifier=request.organization_identifier,
        )
        if not has_workspace_access:
            return self._decision(
                allowed=False,
                reason="Workspace isolation denied access",
                missing_permissions=(),
                missing_capabilities=(),
                policy_decision=self.policy_engine.evaluate(
                    self._to_policy_request(request),
                ),
            )

        has_organization_access = (
            request.organization_identifier in context.organization_memberships
            or self.organization_model.is_member(
                context.identity.immutable_id,
                request.organization_identifier,
            )
        )
        if not has_organization_access:
            return self._decision(
                allowed=False,
                reason="Organization membership denied access",
                missing_permissions=(),
                missing_capabilities=(),
                policy_decision=self.policy_engine.evaluate(
                    self._to_policy_request(request),
                ),
            )

        role_permissions = self.role_catalog.resolve_permissions(context.role_names)
        effective_permissions = set(role_permissions).union(context.permission_keys)

        role_capabilities = self.role_catalog.resolve_capabilities(context.role_names)
        effective_capabilities = {capability.key for capability in role_capabilities}.union(
            capability.key for capability in context.capabilities
        )

        ownership_granted = (
            request.owner_identifier is not None
            and request.owner_identifier == context.identity.immutable_id
        )

        missing_permissions = tuple(
            permission
            for permission in request.required_permissions
            if permission not in effective_permissions and not ownership_granted
        )
        missing_capabilities = tuple(
            capability.key
            for capability in request.required_capabilities
            if capability.key not in effective_capabilities
        )

        policy_decision = self.policy_engine.evaluate(self._to_policy_request(request))
        if not policy_decision.allowed:
            return self._decision(
                allowed=False,
                reason=policy_decision.reason,
                missing_permissions=missing_permissions,
                missing_capabilities=missing_capabilities,
                policy_decision=policy_decision,
                ownership_granted=ownership_granted,
            )

        if missing_permissions or missing_capabilities:
            return self._decision(
                allowed=False,
                reason="Missing required permissions or capabilities",
                missing_permissions=missing_permissions,
                missing_capabilities=missing_capabilities,
                policy_decision=policy_decision,
                ownership_granted=ownership_granted,
            )

        return self._decision(
            allowed=True,
            reason="Authorization granted",
            missing_permissions=(),
            missing_capabilities=(),
            policy_decision=policy_decision,
            ownership_granted=ownership_granted,
        )

    def _to_policy_request(self, request: AuthorizationRequest) -> PolicyEvaluationRequest:
        context = request.security_context
        policy_attributes = [
            PolicyAttribute(key=key, value=value)
            for key, value in context.policy_attributes()
        ]
        policy_attributes.extend(request.attributes)
        return PolicyEvaluationRequest(
            actor_identifier=context.identity.immutable_id,
            actor_identity_type=context.identity.identity_type,
            actor_roles=context.role_names,
            workspace_identifier=request.workspace_identifier,
            organization_identifier=request.organization_identifier,
            action=request.action,
            resource=request.resource,
            attributes=tuple(policy_attributes),
        )

    def _decision(
        self,
        *,
        allowed: bool,
        reason: str,
        missing_permissions: tuple[str, ...],
        missing_capabilities: tuple[str, ...],
        policy_decision: PolicyDecision,
        ownership_granted: bool = False,
    ) -> AuthorizationDecision:
        return AuthorizationDecision(
            metadata=new_metadata(
                object_type=SecurityObjectType.AUTHORIZATION_DECISION,
                owner_identifier="system",
            ),
            allowed=allowed,
            reason=reason,
            missing_permissions=missing_permissions,
            missing_capabilities=missing_capabilities,
            policy_decision=policy_decision,
            ownership_granted=ownership_granted,
        )
