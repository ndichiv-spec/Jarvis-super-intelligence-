# Permission Model

The permission manager implements a hierarchical access-control model with
four levels: **NONE < READ < WRITE < ADMIN**.

## Permission Levels

| Level   | Value | Description                        |
|---------|-------|------------------------------------|
| NONE    | 0     | No access (default)                |
| READ    | 1     | Read-only access                   |
| WRITE   | 2     | Read + write access                |
| ADMIN   | 3     | Full control                       |

## Resources

- WORKSPACE, PROJECT, KNOWLEDGE, MEMORY
- TOOL, COMMUNICATION, EXTERNAL_SYSTEM

## Rules

- A higher-level permission automatically satisfies all lower-level checks
  (e.g. WRITE covers both READ and WRITE).
- Wildcard scope (`*`) applies to all scopes.
- Explicit scope overrides wildcard for that scope.

## Usage

```python
from jarvis_tools.permissions import InMemoryPermissionManager
from jarvis_tools.models import ToolPermission, PermissionResource, PermissionAccess

pm = InMemoryPermissionManager()

# Grant
pm.grant_permission("my.tool", ToolPermission(
    resource=PermissionResource.KNOWLEDGE,
    access=PermissionAccess.READ,
))

# Check
assert pm.check_permission("my.tool", "knowledge", "read", "*")
assert not pm.check_permission("my.tool", "knowledge", "write", "*")

# Revoke
pm.revoke_permission("my.tool", "knowledge", "*")
```
