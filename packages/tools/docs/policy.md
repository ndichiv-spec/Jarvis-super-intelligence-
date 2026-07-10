# Policy Engine

The policy engine provides governance rules for tool execution, including
rate limiting, workspace restrictions, and enterprise compliance.

## Policy Fields

| Field                      | Type       | Default | Description                     |
|----------------------------|------------|---------|---------------------------------|
| `max_executions_per_minute`| `int`      | 60      | Rate limit                      |
| `max_concurrent_executions`| `int`      | 10      | Concurrency cap                 |
| `default_timeout_seconds`  | `int`      | 300     | Default execution timeout       |
| `workspace_restrictions`   | `tuple[str]` | `("**",)` | Allowed workspaces           |
| `denied_tools`             | `tuple[str]` | `()`   | Explicitly denied tools         |
| `compliance_tags`          | `frozenset[str]` | `()` | Compliance markers          |

## Scope Matching

Policies are resolved by matching `ToolPolicyScope` fields:

- Owner, workspace, project — exact match or wildcard (`*`).
- Enterprise scope enables additional governance constraints.

## Usage

```python
from jarvis_tools.policy import InMemoryPolicyEngine
from jarvis_tools.models import ToolPolicy, ToolPolicyScope

engine = InMemoryPolicyEngine()
engine.register_policy(
    ToolPolicyScope(workspace="prod", is_enterprise=True),
    ToolPolicy(
        policy_id="prod-policy",
        name="Production Policy",
        max_concurrent_executions=5,
        denied_tools=("code.execution",),
    ),
)
policy = engine.resolve(ToolPolicyScope(workspace="prod"))
violations = engine.evaluate("code.execution", policy)
```
