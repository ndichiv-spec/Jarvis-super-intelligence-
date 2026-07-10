from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_automation.models import AutomationPolicy, AutomationPolicyScope


@dataclass(slots=True)
class InMemoryPolicyEngine:
    _policies: list[tuple[AutomationPolicyScope, AutomationPolicy]] = field(default_factory=list)

    def register_policy(
        self, scope: AutomationPolicyScope, policy: AutomationPolicy,
    ) -> None:
        self._policies = [
            (s, p) for s, p in self._policies if s != scope
        ]
        self._policies.append((scope, policy))

    def resolve(self, scope: AutomationPolicyScope) -> AutomationPolicy:
        matched: list[AutomationPolicy] = []
        for candidate_scope, candidate_policy in self._policies:
            if self._scope_matches(candidate_scope, scope):
                matched.append(candidate_policy)
        if not matched:
            return AutomationPolicy(policy_id="default", name="default")
        return matched[-1]

    def evaluate(
        self, workflow_id: str, policy: AutomationPolicy,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if workflow_id in policy.denied_workflows:
            violations.append(f"Workflow '{workflow_id}' is denied by policy")
        if (
            policy.workspace_restrictions
            and policy.workspace_restrictions != ("*",)
        ):
            violations.append(
                f"Workflow '{workflow_id}' restricted to workspaces: "
                f"{', '.join(policy.workspace_restrictions)}",
            )
        return tuple(violations)

    def _scope_matches(
        self,
        candidate: AutomationPolicyScope,
        target: AutomationPolicyScope,
    ) -> bool:
        if candidate.owner != "*" and candidate.owner != target.owner:
            return False
        if candidate.workspace != "*" and candidate.workspace != target.workspace:
            return False
        if candidate.project != "*" and candidate.project != target.project:
            return False
        return True
