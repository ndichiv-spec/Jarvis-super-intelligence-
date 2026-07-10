from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_tools.models import ToolPolicy, ToolPolicyScope


@dataclass(slots=True)
class InMemoryPolicyEngine:
    _policies: list[tuple[ToolPolicyScope, ToolPolicy]] = field(default_factory=list)

    def register_policy(self, scope: ToolPolicyScope, policy: ToolPolicy) -> None:
        self._policies = [(s, p) for s, p in self._policies if s != scope]
        self._policies.append((scope, policy))

    def resolve(self, scope: ToolPolicyScope) -> ToolPolicy:
        matched: list[ToolPolicy] = []
        for candidate_scope, candidate_policy in self._policies:
            if self._scope_matches(candidate_scope, scope):
                matched.append(candidate_policy)
        if not matched:
            return ToolPolicy(policy_id="default", name="default")
        return matched[-1]

    def evaluate(
        self,
        tool_identifier: str,
        policy: ToolPolicy,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if tool_identifier in policy.denied_tools:
            violations.append(f"Tool '{tool_identifier}' is denied by policy")
        if policy.workspace_restrictions and policy.workspace_restrictions != ("*",):
            violations.append(
                f"Tool '{tool_identifier}' restricted to workspaces: "
                f"{', '.join(policy.workspace_restrictions)}",
            )
        return tuple(violations)

    def _scope_matches(
        self,
        candidate: ToolPolicyScope,
        target: ToolPolicyScope,
    ) -> bool:
        if candidate.owner != "*" and candidate.owner != target.owner:
            return False
        if candidate.workspace != "*" and candidate.workspace != target.workspace:
            return False
        if candidate.project != "*" and candidate.project != target.project:
            return False
        return True
