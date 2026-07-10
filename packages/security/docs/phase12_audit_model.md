# Phase 12 Audit Model

## Audit Domains

- Authentication
- Authorization
- Policy decisions
- Workflow execution
- Tool usage
- Agent activity
- Extension lifecycle
- Configuration changes

## Event Structure

Each event is immutable and includes:

- Metadata
- Event type
- Actor identifier
- Target identifier
- Timestamp
- Summary
- Typed key/value details

## Audit Coordination

Security Kernel records governance-significant events automatically for:

- Identity and policy configuration changes
- Context issuance
- Authorization decisions
- Policy evaluation outcomes
