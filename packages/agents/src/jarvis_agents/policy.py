from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.models import AgentMetadata, AgentPolicy, AgentPolicyScope, AgentStatus


@dataclass(slots=True)
class DefaultPolicyEngine:
    _policies: dict[tuple[str, str, str], AgentPolicy] = field(default_factory=dict)

    def register_policy(self, scope: AgentPolicyScope, policy: AgentPolicy) -> None:
        self._policies[(scope.owner, scope.workspace, scope.project)] = policy

    def resolve(self, scope: AgentPolicyScope) -> AgentPolicy:
        key = (scope.owner, scope.workspace, scope.project)
        policy = self._policies.get(key)
        if policy is not None:
            return policy
        if scope.is_enterprise:
            return AgentPolicy(
                policy_id="enterprise-default",
                name="Enterprise Default",
                workspace_isolation=True,
                enterprise_governance=True,
                max_concurrent_tasks=10,
                max_retries_per_task=5,
            )
        return AgentPolicy(policy_id="agent-default", name="Agent Default Policy")

    def evaluate(self, *, agent: AgentMetadata, policy: AgentPolicy) -> tuple[str, ...]:
        violations: list[str] = []
        if agent.status == AgentStatus.FAILED:
            violations.append("Agent is in failed state")
        denied = [c.name for c in agent.capabilities if c.name in policy.denied_capabilities]
        if denied:
            violations.append(f"Capabilities denied by policy: {', '.join(denied)}")
        if policy.allowed_capabilities != ("*",):
            for cap in agent.capabilities:
                if cap.name not in policy.allowed_capabilities:
                    violations.append(f"Capability not allowed: {cap.name}")
        return tuple(violations)
