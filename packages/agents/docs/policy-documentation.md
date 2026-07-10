# Policy Engine

## Overview

The `PolicyEngine` provides configurable governance for agents. Policies are resolved by scope (owner, workspace, project) and evaluated against agent capabilities and status.

## Policy Model

```python
@dataclass(frozen=True, slots=True)
class AgentPolicy:
    policy_id: str
    name: str
    workspace_isolation: bool = True
    enterprise_governance: bool = False
    max_concurrent_tasks: int = 5
    max_retries_per_task: int = 3
    rate_limit_per_minute: int = 60
    execution_timeout_seconds: int = 3600
    allowed_capabilities: tuple[str, ...] = ("*",)
    denied_capabilities: tuple[str, ...] = ()
    compliance_tags: frozenset[str] = frozenset()
```

## Scope Resolution

Policies are stored and resolved by a composite key of `(owner, workspace, project)`. The resolution order:

1. Exact match on `(owner, workspace, project)`
2. Enterprise fallback (if `scope.is_enterprise`)
3. Default policy (`"agent-default"`)

## Evaluation Rules

The `evaluate()` method checks:

1. **Failed state** — If the agent's status is `FAILED`, a violation is recorded.
2. **Denied capabilities** — Any capability present in `denied_capabilities` triggers a violation.
3. **Allowed capabilities** — If `allowed_capabilities` is not `("*",)`, any capability not in the allowed set triggers a violation.

## Usage

```python
from jarvis_agents import AgentPolicy, AgentPolicyScope, DefaultPolicyEngine

engine = DefaultPolicyEngine()

# Register a custom policy
scope = AgentPolicyScope(owner="user1", workspace="project-x")
policy = AgentPolicy(
    policy_id="pol-strict",
    name="Strict Policy",
    allowed_capabilities=("research", "analysis"),
    denied_capabilities=("automation",),
    max_concurrent_tasks=2,
)
engine.register_policy(scope, policy)

# Resolve and evaluate
resolved = engine.resolve(scope)
violations = engine.evaluate(agent=agent, policy=resolved)
```

Through the kernel:

```python
kernel.register_policy(scope, policy)
violations = kernel.evaluate_policy("agent-001")
```
