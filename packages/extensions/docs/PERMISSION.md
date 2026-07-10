# Permission Model

## Overview

The permission system defines what resources and operations an extension may access. Permissions are declared in the extension manifest and granted at activation time. The system provides contracts for permission management; authorization policy implementation (approval workflows, user prompts) is deferred to the Security subsystem.

## Permission Scopes

```python
class PermissionScope(Enum):
    MEMORY_ACCESS = auto()          # Read/write the JARVIS memory store
    KNOWLEDGE_ACCESS = auto()       # Read/write knowledge sources
    TOOL_REGISTRATION = auto()      # Register tools with the Tool Platform
    WORKFLOW_REGISTRATION = auto()  # Register workflow templates
    WORKSPACE_ACCESS = auto()       # Access workspace files and state
    EVENT_SUBSCRIPTION = auto()     # Subscribe to system events
    COMMAND_REGISTRATION = auto()   # Register executable commands
```

## PermissionRequest

```python
@dataclass(frozen=True, slots=True)
class PermissionRequest:
    permission_scope: PermissionScope  # What is being requested
    reason: str = ""                   # Justification for the request
    required: bool = True              # Whether this permission is mandatory
```

- `required=True`: The extension cannot function without this permission.
- `required=False`: The permission is optional; the extension may degrade gracefully.

## PermissionManager API

```python
# Grant a permission to an extension
pm.grant("ext1", PermissionRequest(scope=PermissionScope.TOOL_REGISTRATION))

# Check if a permission is granted
pm.check("ext1", PermissionScope.TOOL_REGISTRATION)  # True

# Revoke a specific permission
pm.revoke("ext1", PermissionScope.TOOL_REGISTRATION)

# List all granted permissions
pm.list_permissions("ext1")

# Revoke all permissions for an extension
pm.revoke_all("ext1")
```

## Lifecycle Integration

During `ExtensionKernel.activate()`, all permissions declared in the manifest are automatically granted:

```python
for perm in meta.manifest.permissions:
    self.permissions.grant(extension_id, perm)
```

During `ExtensionKernel.disable()`, all permissions are revoked:

```python
self.permissions.revoke_all(extension_id)
```

## Built-in Extension Permissions

The 8 built-in extensions declare permissions appropriate to their type:

| Extension | Permission | Reason |
|-----------|------------|--------|
| AI Providers | COMMAND_REGISTRATION | Register AI provider commands |
| Knowledge Connector | KNOWLEDGE_ACCESS | Access knowledge sources |
| Tool Pack | TOOL_REGISTRATION, WORKSPACE_ACCESS | Register tools, access workspace |
| Automation Pack | WORKFLOW_REGISTRATION | Register workflow templates |
| Enterprise Integration | COMMAND_REGISTRATION | Register enterprise integration commands |

## Edge Cases

- Querying permissions for a non-existent extension returns `False` for `check()` and empty tuple for `list_permissions()`.
- `revoke_all` on an extension with no permissions is a no-op (no error).
