# Permission Model

## Permission Types (15 Types)

The `PermissionCenter` defines 15 permission types in `PermissionType` enum:

| # | Permission | Enum Variant | Description | Frontend Type |
|---|-----------|-------------|-------------|---------------|
| 1 | **File System Read** | `FileSystemRead` | Read files on the local file system | `file:read` |
| 2 | **File System Write** | `FileSystemWrite` | Write files to the local file system | `file:write` |
| 3 | **Folder Select** | *(granted via File dialog)* | Select folders from the file system | `folder:select` |
| 4 | **Clipboard Read** | `ClipboardRead` | Read from the system clipboard | `clipboard:read` |
| 5 | **Clipboard Write** | `ClipboardWrite` | Write to the system clipboard | `clipboard:write` |
| 6 | **Network Access** | `NetworkAccess` | Make network requests | `network:connect` |
| 7 | **Notification Send** | `NotificationSend` | Send desktop notifications | `notification:send` |
| 8 | **Microphone Access** | `MicrophoneAccess` | Access the microphone | `microphone:access` |
| 9 | **Camera Access** | `CameraAccess` | Access the camera | `camera:access` |
| 10 | **Location Access** | `LocationAccess` | Access location data | — |
| 11 | **Gateway Connect** | `GatewayConnect` | Connect to the JARVIS AI Gateway | — |
| 12 | **Sync Access** | `SyncAccess` | Access workspace sync functionality | — |
| 13 | **Settings Read/Write** | `SettingsRead`, `SettingsWrite` | Read/modify application settings | — |
| 14 | **Execute Command** | `ExecuteCommand` | Execute privileged commands | `integration:launch` |
| 15 | **Audit View** | `AuditView` | View audit logs | — |

## Permission Lifecycle

Every permission follows a four-stage lifecycle:

```
   REQUEST ──►  PENDING  ──►  GRANTED  ──►  REVOKED
                   │                              │
                   └──►  DENIED                    │
                                                   │
                                         [Optional] EXPIRED
                                                   │
                                              (future: time-bound)
```

### Stage 1: Request

A module or command requests a permission with a reason:

```rust
let req = permission_center.request(
    PermissionType::FileSystemRead,
    "Open document for analysis"
);
// Creates a PermissionRequest with status: Pending
// Logs audit event: "requested"
```

### Stage 2: Pending Review

The request appears in the Permission Center UI. The user sees:

- Permission type and description
- Resource requested
- Reason for the request
- Source module
- Timestamp

### Stage 3: Grant or Deny

The user approves or denies via the UI:

```rust
// Grant
permission_center.grant(&request_id);
// Creates PermissionGrant, logs "granted" audit event

// Deny
permission_center.deny(&request_id);
// Logs "denied" audit event
```

### Stage 4: Revoke

At any time, the user can revoke a previously granted permission:

```rust
permission_center.revoke(&grant_id);
// Removes grant, logs "revoked" audit event
```

## Explicit Authorization Flow

All privileged operations follow this pattern:

```
Frontend Component
    │
    ├── 1. Check if permission is granted
    │
    ├── 2. If not granted:
    │      └── request_permission(type, reason)
    │           └── Opens Permission Request dialog
    │                └── User approves/denies
    │
    └── 3. If granted:
           └── Execute the operation
                └── Operation logged to audit
```

## Revocable Permissions

Permissions can be revoked at any time through:

1. **Permission Center UI** — user manually revokes a grant
2. **Session end** — some permissions are session-scoped (future)
3. **Expiration** — time-bound grants (future)

Once revoked, the corresponding operation will fail at step 1 above and re-prompt the user.

## Permission Storage and Persistence

Permissions are stored in-memory within the `PermissionCenter` managed state. The structure comprises three lists:

| List | Type | Purpose |
|------|------|---------|
| `grants` | `Vec<PermissionGrant>` | Currently active permissions |
| `requests` | `Vec<PermissionRequest>` | All requests (including historical) |
| `history` | `Vec<PermissionEvent>` | Immutable audit trail |

Persistence is implicit through the audit log and the user-facing Permission Center state.

## Audit Integration

Every permission action generates an `AuditEvent`:

| Action | Module | Success |
|--------|--------|---------|
| Permission requested | `permissions` | `true` |
| Permission granted | `permissions` | `true` |
| Permission denied | `permissions` | `false` |
| Permission revoked | `permissions` | `true` |

Audit events include the permission type, timestamp, and outcome.

## Privacy Rules

The permission model enforces these privacy principles:

1. **No Auto-Scanning** — The application never scans the file system without explicit user permission. File operations are always user-initiated via the native file dialog.

2. **No Background Surveillance** — Clipboard access, camera, microphone, and location require explicit per-session approval. No continuous monitoring.

3. **No Continuous Monitoring** — All permissions are single-use or session-scoped. There is no background daemon that monitors system state.

4. **Telemetry Opt-In** — Telemetry collection is disabled by default (`PrivacySettings::collect_telemetry = false`).

5. **Local Processing Mode** — When enabled, all processing stays on-device and no data is sent to the Gateway.

## Permission Flow Examples

### File Read

```
User clicks "Open File" in chat
    → UI checks file:read permission
    → Not granted → request_permission("file:read", "Open document")
    → Pending request appears in Permission Center
    → User grants via UI
    → invoke("open_file") → Native file dialog opens
    → File path returned to frontend
    → Operation logged to audit
```

### Clipboard Write

```
AI agent generates code snippet
    → UI checks clipboard:write permission
    → Not granted → request_permission("clipboard:write", "Copy code to clipboard")
    → Pending request appears in Permission Center
    → User approves
    → invoke("copy_to_clipboard") → ClipboardManager plugin writes
    → Audit logged: "clipboard.write"
```

### Notification Send

```
Workflow completes
    → UI checks notification:send permission
    → If granted, invoke("send_notification", ...)
    → Native OS notification displayed
    → Audit logged: "notification.send"
```

### Integration Launch

```
User triggers "Open in VS Code"
    → UI checks integration:launch permission
    → If not granted → Permission request dialog
    → User approves → Shell plugin launches VS Code
    → Audit logged
```
