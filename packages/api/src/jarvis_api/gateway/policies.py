from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.protocol_registry import ProtocolDescriptor
from jarvis_api.gateway.routing import RouteDefinition
from jarvis_api.gateway.types import GatewayRequest, ProtocolName, Protocols, SubsystemName
from jarvis_api.gateway.versioning import ApiVersion


@dataclass(frozen=True, slots=True)
class GatewayPolicy:
    restricted_protocols: tuple[ProtocolName, ...] = field(default_factory=tuple)
    workspace_subsystem_rules: Mapping[str, tuple[SubsystemName, ...]] = field(default_factory=dict)
    streaming_protocol_allowlist: tuple[ProtocolName, ...] = (
        Protocols.REST,
        Protocols.WEBSOCKET,
        Protocols.SSE,
        Protocols.MCP,
    )
    minimum_version: ApiVersion | None = None
    maximum_version: ApiVersion | None = None
    enterprise_governance: Mapping[str, str] = field(default_factory=dict)


class GatewayPolicyEngine:
    def __init__(self, policy: GatewayPolicy | None = None) -> None:
        self._policy = policy or GatewayPolicy()

    def enforce(
        self,
        request: GatewayRequest,
        *,
        route: RouteDefinition,
        resolved_version: ApiVersion,
        protocol_descriptor: ProtocolDescriptor,
    ) -> None:
        del protocol_descriptor

        if request.protocol in self._policy.restricted_protocols:
            raise GatewayException.policy_violation(
                f"Protocol '{request.protocol}' is restricted by gateway policy",
                details={"protocol": request.protocol},
            )

        if request.workspace_id and request.workspace_id in self._policy.workspace_subsystem_rules:
            allowed_subsystems = self._policy.workspace_subsystem_rules[request.workspace_id]
            if route.subsystem not in allowed_subsystems:
                message = (
                    f"Workspace '{request.workspace_id}' cannot access "
                    f"subsystem '{route.subsystem}'"
                )
                raise GatewayException.policy_violation(
                    message,
                    details={
                        "workspace_id": request.workspace_id,
                        "subsystem": route.subsystem,
                    },
                )

        if (
            request.stream is not None
            and request.protocol not in self._policy.streaming_protocol_allowlist
        ):
            raise GatewayException.policy_violation(
                f"Streaming is not allowed for protocol '{request.protocol}'",
                details={"protocol": request.protocol},
            )

        if self._policy.minimum_version and resolved_version < self._policy.minimum_version:
            raise GatewayException.policy_violation(
                "API version is below policy minimum",
                details={
                    "minimum": str(self._policy.minimum_version),
                    "resolved": str(resolved_version),
                },
            )

        if self._policy.maximum_version and resolved_version > self._policy.maximum_version:
            raise GatewayException.policy_violation(
                "API version is above policy maximum",
                details={
                    "maximum": str(self._policy.maximum_version),
                    "resolved": str(resolved_version),
                },
            )

        require_workspace = self._policy.enterprise_governance.get("require_workspace") == "true"
        if require_workspace and request.workspace_id is None:
            raise GatewayException.policy_violation(
                "Workspace is required by enterprise governance policy",
                details={"governance": "require_workspace"},
            )

        require_identity = self._policy.enterprise_governance.get("require_identity") == "true"
        if require_identity and request.subject_id is None:
            raise GatewayException.policy_violation(
                "Identity is required by enterprise governance policy",
                details={"governance": "require_identity"},
            )
