"""Cloud Security Integration - secrets injection, service identities, network policies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SecretInjectionMethod(StrEnum):
    environment = "environment"
    volume = "volume"
    sidecar = "sidecar"
    vault_agent = "vault_agent"


class NetworkPolicyMode(StrEnum):
    permissive = "permissive"
    default_deny = "default_deny"
    least_privilege = "least_privilege"
    zero_trust = "zero_trust"


@dataclass(frozen=True)
class ServiceIdentity:
    service_name: str
    identity_type: str = "service-account"
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SecretReference:
    name: str
    key: str
    mount_path: str | None = None
    env_var: str | None = None
    injection: SecretInjectionMethod = SecretInjectionMethod.environment


@dataclass(frozen=True)
class NetworkPolicyRule:
    from_service: str
    to_service: str
    ports: list[int]
    protocol: str = "TCP"


@dataclass(frozen=True)
class CloudSecurityConfig:
    secrets: list[SecretReference] = field(default_factory=list)
    identities: list[ServiceIdentity] = field(default_factory=list)
    network_policy_mode: NetworkPolicyMode = NetworkPolicyMode.default_deny
    network_policies: list[NetworkPolicyRule] = field(default_factory=list)
    tls_enabled: bool = True
    mTLS_enabled: bool = False
    pod_security_context: dict[str, Any] = field(default_factory=lambda: {"runAsNonRoot": True, "runAsUser": 1000})


DEFAULT_NETWORK_POLICIES: list[NetworkPolicyRule] = [
    NetworkPolicyRule(from_service="ingress", to_service="api", ports=[8000]),
    NetworkPolicyRule(from_service="api", to_service="brain", ports=[8100]),
    NetworkPolicyRule(from_service="api", to_service="ai", ports=[8200]),
    NetworkPolicyRule(from_service="api", to_service="memory", ports=[8300]),
    NetworkPolicyRule(from_service="api", to_service="knowledge", ports=[8400]),
    NetworkPolicyRule(from_service="api", to_service="automation", ports=[8500]),
    NetworkPolicyRule(from_service="api", to_service="agents", ports=[8600]),
    NetworkPolicyRule(from_service="api", to_service="orchestration", ports=[8700]),
    NetworkPolicyRule(from_service="brain", to_service="ai", ports=[8200]),
    NetworkPolicyRule(from_service="orchestration", to_service="brain", ports=[8100]),
    NetworkPolicyRule(from_service="automation", to_service="api", ports=[8000]),
    NetworkPolicyRule(from_service="brain", to_service="redis", ports=[6379]),
    NetworkPolicyRule(from_service="api", to_service="postgres", ports=[5432]),
    NetworkPolicyRule(from_service="memory", to_service="qdrant", ports=[6333]),
    NetworkPolicyRule(from_service="knowledge", to_service="qdrant", ports=[6333]),
]


class CloudSecurityIntegration:
    def __init__(self) -> None:
        self._config = CloudSecurityConfig(
            network_policies=list(DEFAULT_NETWORK_POLICIES),
        )

    @property
    def config(self) -> CloudSecurityConfig:
        return self._config

    def add_secret(self, name: str, key: str, env_var: str, injection: SecretInjectionMethod = SecretInjectionMethod.environment) -> None:
        ref = SecretReference(name=name, key=key, env_var=env_var, injection=injection)
        self._config = CloudSecurityConfig(
            secrets=list(self._config.secrets) + [ref],
            identities=self._config.identities,
            network_policy_mode=self._config.network_policy_mode,
            network_policies=self._config.network_policies,
            tls_enabled=self._config.tls_enabled,
            mTLS_enabled=self._config.mTLS_enabled,
        )

    def generate_network_policy_yaml(self) -> str:
        lines = ["kind: NetworkPolicy", "apiVersion: networking.k8s.io/v1", "metadata:", f"  name: jarvis-network-policy", "spec:"]
        if self._config.network_policy_mode == NetworkPolicyMode.default_deny:
            lines.append("  podSelector: {}")
            lines.append("  policyTypes:")
            lines.append("  - Ingress")
            lines.append("  - Egress")
        else:
            lines.append("  podSelector:")
            lines.append("    matchLabels:")
            lines.append("      app.kubernetes.io/part-of: jarvis")
            lines.append("  policyTypes:")
            lines.append("  - Ingress")
            lines.append("  ingress:")
            for rule in self._config.network_policies:
                lines.append(f"  - from:")
                lines.append(f"    - podSelector:")
                lines.append(f"        matchLabels:")
                lines.append(f"          app: {rule.from_service}")
                lines.append(f"    ports:")
                for port in rule.ports:
                    lines.append(f"    - protocol: {rule.protocol}")
                    lines.append(f"      port: {port}")
        return "\n".join(lines)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self._config.network_policies and self._config.network_policy_mode == NetworkPolicyMode.least_privilege:
            issues.append("Least privilege mode requires network policies")
        for sr in self._config.secrets:
            if not sr.env_var and not sr.mount_path:
                issues.append(f"Secret '{sr.name}/{sr.key}' has no env_var or mount_path")
        return issues
