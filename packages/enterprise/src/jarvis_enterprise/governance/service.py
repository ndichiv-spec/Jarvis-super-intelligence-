"""Enterprise governance service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.governance.models import (
    ComplianceControl,
    DataGovernanceRule,
    GovernancePolicy,
    PolicyEffect,
    PolicyRule,
    PolicyScope,
    PolicyType,
    RetentionPolicy,
)
from jarvis_enterprise.governance.repository import GovernanceRepository


class EnterpriseGovernanceService:
    def __init__(self, repository: GovernanceRepository) -> None:
        self._repository = repository

    def create_policy(
        self, name: str, description: str, scope: PolicyScope,
        policy_type: PolicyType = PolicyType.operational,
        rules: tuple[PolicyRule, ...] = (),
    ) -> GovernancePolicy:
        policy = GovernancePolicy(name=name, description=description, scope=scope, policy_type=policy_type, rules=rules)
        self._repository.save_policy(policy)
        return policy

    def get_policy(self, policy_id: UUID) -> GovernancePolicy | None:
        return self._repository.get_policy(policy_id)

    def list_policies(self, scope: PolicyScope | None = None) -> list[GovernancePolicy]:
        return self._repository.list_policies(scope)

    def enable_policy(self, policy_id: UUID) -> GovernancePolicy | None:
        policy = self._repository.get_policy(policy_id)
        if policy is None:
            return None
        updated = GovernancePolicy(
            id=policy.id, name=policy.name, description=policy.description,
            scope=policy.scope, policy_type=policy.policy_type, enabled=True,
            rules=policy.rules, tags=policy.tags, metadata=policy.metadata,
            created_at=policy.created_at,
        )
        self._repository.save_policy(updated)
        return updated

    def disable_policy(self, policy_id: UUID) -> GovernancePolicy | None:
        policy = self._repository.get_policy(policy_id)
        if policy is None:
            return None
        updated = GovernancePolicy(
            id=policy.id, name=policy.name, description=policy.description,
            scope=policy.scope, policy_type=policy.policy_type, enabled=False,
            rules=policy.rules, tags=policy.tags, metadata=policy.metadata,
            created_at=policy.created_at,
        )
        self._repository.save_policy(updated)
        return updated

    def create_data_rule(self, data_type: str, classification: str, retention_days: int) -> DataGovernanceRule:
        rule = DataGovernanceRule(data_type=data_type, classification=classification, retention_days=retention_days)
        self._repository.save_data_rule(rule)
        return rule

    def create_retention_policy(self, name: str, data_category: str, retention_days: int) -> RetentionPolicy:
        policy = RetentionPolicy(name=name, data_category=data_category, retention_days=retention_days)
        self._repository.save_retention_policy(policy)
        return policy

    def create_compliance_control(self, framework: str, control_id: str, description: str) -> ComplianceControl:
        control = ComplianceControl(framework=framework, control_id=control_id, description=description)
        self._repository.save_compliance_control(control)
        return control

    def evaluate_policies(self, action: str, resource: str, scope_id: UUID | None = None) -> list[GovernancePolicy]:
        matching: list[GovernancePolicy] = []
        for policy in self._repository.list_policies():
            if not policy.enabled:
                continue
            for rule in policy.rules:
                if _match_pattern(rule.resource_pattern, resource) and _match_pattern(rule.action_pattern, action):
                    matching.append(policy)
        return matching


def _match_pattern(pattern: str, value: str) -> bool:
    if pattern == "*":
        return True
    if pattern.endswith("*") and value.startswith(pattern[:-1]):
        return True
    return pattern == value
