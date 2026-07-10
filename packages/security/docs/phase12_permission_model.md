# Phase 12 Permission Model

## Domains

- Memory
- Knowledge
- Agents
- Tools
- Automation
- Extensions
- Projects
- Workspaces
- Future infrastructure

## Permission Key Format

Permissions are normalized as:

`domain:action:resource`

Example:

`tools:execute:*`

## Role Integration

- Roles resolve into permission keys.
- Custom roles can inherit from predefined roles.
- Effective permissions are role-derived plus explicit grants.

## Governance Notes

- Permissions are metadata-backed immutable objects.
- Authorization decisions include missing permissions for auditability.
