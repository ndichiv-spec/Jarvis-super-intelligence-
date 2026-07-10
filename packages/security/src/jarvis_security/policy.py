from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from fnmatch import fnmatchcase

from jarvis_security.identity import IdentityType
from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class PolicyType(Enum):
    PASSWORD = auto()
    WORKSPACE = auto()
    RETENTION = auto()
    EXECUTION = auto()
    EXTENSION = auto()
    RESOURCE = auto()
    ENTERPRISE_GOVERNANCE = auto()


class PolicyEffect(Enum):
    ALLOW = auto()
    DENY = auto()
    CONDITIONAL = auto()


class ComparisonOperator(Enum):
    EQUALS = auto()
    NOT_EQUALS = auto()
    PREFIX = auto()
    CONTAINS = auto()


@dataclass(frozen=True, slots=True)
class PolicyAttribute:
    key: str
    value: str

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("key cannot be empty")


@dataclass(frozen=True, slots=True)
class PolicyCondition:
    attribute: str
    operator: ComparisonOperator
    expected: str

    def __post_init__(self) -> None:
        if not self.attribute.strip():
            raise ValueError("attribute cannot be empty")

    def matches(self, attributes: dict[str, str]) -> bool:
        actual = attributes.get(self.attribute)
        if actual is None:
            return False
        if self.operator is ComparisonOperator.EQUALS:
            return actual == self.expected
        if self.operator is ComparisonOperator.NOT_EQUALS:
            return actual != self.expected
        if self.operator is ComparisonOperator.PREFIX:
            return actual.startswith(self.expected)
        return self.expected in actual


@dataclass(frozen=True, slots=True)
class PolicyRule:
    metadata: SecurityMetadata
    name: str
    policy_type: PolicyType
    effect: PolicyEffect
    action_pattern: str = "*"
    resource_pattern: str = "*"
    applies_to_roles: tuple[str, ...] = ()
    applies_to_identity_types: tuple[IdentityType, ...] = ()
    conditions: tuple[PolicyCondition, ...] = ()
    priority: int = 0

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.POLICY:
            raise ValueError("metadata.object_type must be policy")
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.action_pattern.strip():
            raise ValueError("action_pattern cannot be empty")
        if not self.resource_pattern.strip():
            raise ValueError("resource_pattern cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        name: str,
        policy_type: PolicyType,
        effect: PolicyEffect,
        owner_identifier: str,
        action_pattern: str = "*",
        resource_pattern: str = "*",
        applies_to_roles: tuple[str, ...] = (),
        applies_to_identity_types: tuple[IdentityType, ...] = (),
        conditions: tuple[PolicyCondition, ...] = (),
        priority: int = 0,
    ) -> PolicyRule:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.POLICY,
                owner_identifier=owner_identifier,
            ),
            name=name,
            policy_type=policy_type,
            effect=effect,
            action_pattern=action_pattern,
            resource_pattern=resource_pattern,
            applies_to_roles=applies_to_roles,
            applies_to_identity_types=applies_to_identity_types,
            conditions=conditions,
            priority=priority,
        )


@dataclass(frozen=True, slots=True)
class PolicyEvaluationRequest:
    actor_identifier: str
    actor_identity_type: IdentityType
    actor_roles: tuple[str, ...]
    workspace_identifier: str
    organization_identifier: str
    action: str
    resource: str
    attributes: tuple[PolicyAttribute, ...] = ()

    def __post_init__(self) -> None:
        if not self.actor_identifier.strip():
            raise ValueError("actor_identifier cannot be empty")
        if not self.workspace_identifier.strip():
            raise ValueError("workspace_identifier cannot be empty")
        if not self.organization_identifier.strip():
            raise ValueError("organization_identifier cannot be empty")
        if not self.action.strip():
            raise ValueError("action cannot be empty")
        if not self.resource.strip():
            raise ValueError("resource cannot be empty")


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    metadata: SecurityMetadata
    allowed: bool
    effect: PolicyEffect
    reason: str
    matched_rule_identifiers: tuple[str, ...]
    evaluated_at: datetime


@dataclass(slots=True)
class PolicyEngine:
    _rules: list[PolicyRule] = field(default_factory=list)

    def register_rule(self, rule: PolicyRule) -> PolicyRule:
        self._rules.append(rule)
        return rule

    def list_rules(self) -> tuple[PolicyRule, ...]:
        return tuple(self._rules)

    def evaluate(self, request: PolicyEvaluationRequest) -> PolicyDecision:
        matched_rules = [
            rule
            for rule in self._sorted_rules()
            if self._matches_rule(rule=rule, request=request)
        ]
        if not matched_rules:
            return self._decision(
                allowed=True,
                effect=PolicyEffect.ALLOW,
                reason="No matching policy rule",
                matched_rule_identifiers=(),
            )

        first_deny = next(
            (
                rule
                for rule in matched_rules
                if rule.effect is PolicyEffect.DENY
            ),
            None,
        )
        if first_deny is not None:
            return self._decision(
                allowed=False,
                effect=PolicyEffect.DENY,
                reason=f"Denied by policy: {first_deny.name}",
                matched_rule_identifiers=(first_deny.metadata.identifier,),
            )

        first_allow = next(
            (
                rule
                for rule in matched_rules
                if rule.effect in {PolicyEffect.ALLOW, PolicyEffect.CONDITIONAL}
            ),
            None,
        )
        if first_allow is not None:
            return self._decision(
                allowed=True,
                effect=first_allow.effect,
                reason=f"Allowed by policy: {first_allow.name}",
                matched_rule_identifiers=(first_allow.metadata.identifier,),
            )

        return self._decision(
            allowed=False,
            effect=PolicyEffect.DENY,
            reason="No allow policy matched",
            matched_rule_identifiers=tuple(rule.metadata.identifier for rule in matched_rules),
        )

    def _sorted_rules(self) -> tuple[PolicyRule, ...]:
        return tuple(
            sorted(
                self._rules,
                key=lambda item: (-item.priority, item.metadata.identifier),
            ),
        )

    def _matches_rule(
        self,
        *,
        rule: PolicyRule,
        request: PolicyEvaluationRequest,
    ) -> bool:
        if (
            rule.applies_to_roles
            and not set(request.actor_roles).intersection(rule.applies_to_roles)
        ):
            return False
        if (
            rule.applies_to_identity_types
            and request.actor_identity_type not in rule.applies_to_identity_types
        ):
            return False
        if not fnmatchcase(request.action, rule.action_pattern):
            return False
        if not fnmatchcase(request.resource, rule.resource_pattern):
            return False
        attributes = {attribute.key: attribute.value for attribute in request.attributes}
        return all(condition.matches(attributes) for condition in rule.conditions)

    def _decision(
        self,
        *,
        allowed: bool,
        effect: PolicyEffect,
        reason: str,
        matched_rule_identifiers: tuple[str, ...],
    ) -> PolicyDecision:
        decision_time = datetime.now(tz=UTC)
        return PolicyDecision(
            metadata=new_metadata(
                object_type=SecurityObjectType.POLICY,
                owner_identifier="system",
            ),
            allowed=allowed,
            effect=effect,
            reason=reason,
            matched_rule_identifiers=matched_rule_identifiers,
            evaluated_at=decision_time,
        )
