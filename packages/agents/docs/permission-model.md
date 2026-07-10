# Permission Model

## Access Levels

Permissions follow a hierarchical numeric model:

| Level | Value | Description |
|-------|-------|-------------|
| NONE  | 0     | No access |
| READ  | 1     | Read-only access |
| WRITE | 2     | Read and write access |
| ADMIN | 3     | Full administrative access |

Higher levels implicitly grant all lower levels. `ADMIN` grants `READ`, `WRITE`, and `ADMIN`.

## Resources

| Resource | Description |
|----------|-------------|
| `memory` | Per-agent key-value memory store |
| `knowledge` | Shared document/knowledge store |
| `tool` | External tool access |
| `project` | Project-level resources |
| `workspace` | Workspace-level resources |
| `communication` | Inter-agent communications |
| `external_system` | External system integration |

## Permission Evaluation

Permissions are evaluated against two sources:

1. **Agent-level permissions** — defined on the `AgentMetadata.permissions` tuple at registration time.
2. **Runtime grants** — dynamically added via `PermissionManager.grant_permission()`.

Access is granted if **any** permission on either source satisfies the required resource, access level, and scope.

## Scope Isolation

Each permission carries a `scope` string (default `"*"`). A permission only grants access when the scope matches the request scope. This enables workspace-level isolation.

```python
from jarvis_agents.models import AgentPermission, AgentPermissionResource, PermissionAccess

perm = AgentPermission(
    resource=AgentPermissionResource.MEMORY,
    access=PermissionAccess.READ,
    scope="project-alpha",
)
# Only grants MEMORY READ within "project-alpha"
```

## Usage

```python
# Check permission through kernel
if kernel.check_permission("agent-001", "memory", "write", "my-workspace"):
    kernel.store_memory("agent-001", "key", "value")

# Grant additional permissions at runtime
kernel._permission_manager.grant_permission(
    "agent-001",
    AgentPermission(resource=AgentPermissionResource.TOOL, access=PermissionAccess.READ),
)
```
