# Phase 12 Policy Model

## Policy Types

- Password
- Workspace
- Retention
- Execution
- Extension
- Resource
- Enterprise governance

## Evaluation Model

- Rules use action/resource pattern matching.
- Rules can be role-targeted and identity-type targeted.
- Rules can include attribute-based conditions.
- Deny rules take precedence over allow/conditional rules.

## Decision Output

Policy decisions provide:

- Allowed or denied
- Applied effect
- Human-readable reason
- Matched rule identifiers
- Evaluation timestamp

## ABAC Readiness

The policy model supports future ABAC expansion via typed policy attributes
and condition operators.
