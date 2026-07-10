# Enterprise Governance Guide

## Policy Model

The Enterprise Platform implements a hierarchical policy model with three scopes:

```
Global Policies        → Apply to ALL organizations
Organization Policies  → Apply to a specific organization
Workspace Policies     → Apply to a specific workspace
```

Policies are evaluated with deny-by-default semantics — if no policy explicitly allows an action, it is denied.

## Creating Governance Policies

### Global Policy
```python
from jarvis_enterprise.governance.models import PolicyScope, PolicyType, PolicyRule, PolicyEffect
from jarvis_enterprise.governance.service import EnterpriseGovernanceService

governance = EnterpriseGovernanceService(repository)

policy = governance.create_policy(
    name="Data Classification",
    description="All data must be classified before storage",
    scope=PolicyScope.global_,
    policy_type=PolicyType.data_governance,
    rules=(
        PolicyRule(
            resource_pattern="knowledge.*",
            action_pattern="create",
            effect=PolicyEffect.require,
            conditions={"classification": {"required": True}}
        ),
    )
)
```

### Organization Policy
```python
org_policy = governance.create_policy(
    name="Retention Policy",
    description="90-day data retention for compliance",
    scope=PolicyScope.organization,
    policy_type=PolicyType.retention,
)
```

## Policy Evaluation

```python
policies = governance.evaluate_policies(
    action="read",
    resource="knowledge.doc-123",
    scope_id=org.id
)
# Returns all matching enabled policies
```

## Data Governance

### Data Classification Rules
```python
rule = governance.create_data_rule(
    data_type="personal_data",
    classification="confidential",
    retention_days=90
)
```

### Retention Policies
```python
retention = governance.create_retention_policy(
    name="Application Logs",
    data_category="logs",
    retention_days=30
)
```

## Compliance Controls

### Registering Controls
```python
control = governance.create_compliance_control(
    framework="SOC2",
    control_id="CC1.1",
    description="Access control policy is documented and enforced"
)
```

## Policy Lifecycle

1. **Create** — Define policy with scope, type, and rules
2. **Enable/Disable** — Toggle policy enforcement
3. **Evaluate** — Check actions against enabled policies
4. **Audit** — All policy decisions logged to audit trail

Best Practice: Start with audit-mode policies (effect=audit) to understand impact before enforcing deny/require rules.
