"""Tests for Enterprise Governance."""

from uuid import uuid4

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
from jarvis_enterprise.governance.service import EnterpriseGovernanceService


class InMemoryGovernanceRepo:
    def __init__(self):
        self._policies: dict = {}
        self._rules: dict = {}
        self._retention: dict = {}
        self._controls: dict = {}

    def save_policy(self, policy) -> None:
        self._policies[policy.id] = policy

    def get_policy(self, policy_id) -> GovernancePolicy | None:
        return self._policies.get(policy_id)

    def list_policies(self, scope=None) -> list[GovernancePolicy]:
        if scope:
            return [p for p in self._policies.values() if p.scope == scope]
        return list(self._policies.values())

    def delete_policy(self, policy_id) -> None:
        self._policies.pop(policy_id, None)

    def save_data_rule(self, rule) -> None:
        self._rules[rule.id] = rule

    def list_data_rules(self) -> list[DataGovernanceRule]:
        return list(self._rules.values())

    def save_retention_policy(self, policy) -> None:
        self._retention[policy.id] = policy

    def list_retention_policies(self) -> list[RetentionPolicy]:
        return list(self._retention.values())

    def save_compliance_control(self, control) -> None:
        self._controls[control.id] = control

    def list_compliance_controls(self, framework=None) -> list[ComplianceControl]:
        if framework:
            return [c for c in self._controls.values() if c.framework == framework]
        return list(self._controls.values())


class TestGovernanceService:
    def setup_method(self):
        self.repo = EnterpriseGovernanceService(InMemoryGovernanceRepo())

    def test_create_policy(self):
        policy = self.repo.create_policy("Data Retention", "Retain data 90d", PolicyScope.organization)
        assert policy.name == "Data Retention"
        assert policy.scope == PolicyScope.organization

    def test_create_with_rules(self):
        rules = (PolicyRule(resource_pattern="knowledge.*", effect=PolicyEffect.audit),)
        policy = self.repo.create_policy("Audit", "Audit knowledge access", PolicyScope.global_, rules=rules)
        assert len(policy.rules) == 1

    def test_enable_disable(self):
        policy = self.repo.create_policy("Test", "desc", PolicyScope.global_)
        disabled = self.repo.disable_policy(policy.id)
        assert disabled is not None
        assert disabled.enabled is False
        enabled = self.repo.enable_policy(policy.id)
        assert enabled is not None
        assert enabled.enabled is True

    def test_list_policies(self):
        self.repo.create_policy("P1", "desc", PolicyScope.global_)
        self.repo.create_policy("P2", "desc", PolicyScope.organization)
        assert len(self.repo.list_policies()) == 2
        assert len(self.repo.list_policies(PolicyScope.global_)) == 1

    def test_create_data_rule(self):
        rule = self.repo.create_data_rule("user_data", "confidential", 90)
        assert rule.classification == "confidential"

    def test_create_retention_policy(self):
        policy = self.repo.create_retention_policy("Logs", "application_logs", 30)
        assert policy.retention_days == 30

    def test_create_compliance_control(self):
        ctrl = self.repo.create_compliance_control("SOC2", "CC1.1", "Access control policy")
        assert ctrl.framework == "SOC2"

    def test_evaluate_policies(self):
        rules = (PolicyRule(resource_pattern="knowledge.*", action_pattern="read", effect=PolicyEffect.audit),)
        self.repo.create_policy("Audit", "desc", PolicyScope.global_, rules=rules)
        matches = self.repo.evaluate_policies("read", "knowledge.doc")
        assert len(matches) == 1
