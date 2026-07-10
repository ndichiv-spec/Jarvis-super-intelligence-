## Policy Guide

### Policy Domains
- Execution limits (per workflow, per workspace)
- Workspace restrictions and ownership checks
- Concurrency limits
- Rate limits
- Timeout policies
- Enterprise governance controls

### Enforcement Model
- Policies are represented by typed contracts in `models.py`.
- `InMemoryPolicyEngine` evaluates policies before and during execution.
- Violations result in controlled state transitions (`waiting`, `failed`, or `cancelled`) based on policy severity.
