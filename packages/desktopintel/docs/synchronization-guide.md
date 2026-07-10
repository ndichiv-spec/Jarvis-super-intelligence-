# Synchronization Guide

## Sync Modules

The `SyncManager` manages synchronization across four workspace modules:

| Module | Contents | Sync Direction |
|--------|----------|----------------|
| **Projects** | Project structure, metadata, configurations | Bidirectional |
| **Conversations** | Chat history, messages, threads | Bidirectional |
| **Preferences** | User preferences, workspace layout | Bidirectional |
| **Settings** | Desktop, sync, notification, privacy settings | Bidirectional |

## Sync States

Each module tracks its own sync state:

| State | Description | Visual Indicator |
|-------|-------------|-----------------|
| `Synced` | Data is up-to-date with the Gateway | Green checkmark |
| `Syncing` | Sync operation in progress | Spinning indicator |
| `Pending` | Local changes waiting to be synced | Yellow badge |
| `Error(String)` | Sync failed with an error message | Red badge + error text |
| `Offline` | No network connection, sync unavailable | Grey indicator |

The overall sync state aggregates module states:

```
Synced   → All modules synced
Syncing  → Any module syncing
Pending  → Any module has pending changes
Error    → Any module has errors
Offline  → Gateway disconnected
```

## Conflict Resolution

Conflicts occur when the same data is modified both locally and remotely between sync cycles.

### Detection

The sync process compares local and remote timestamps/data hashes for each item. Mismatches are flagged as conflicts.

### Resolution Strategy

Configured via `SyncSettings.conflict_resolution`:

| Strategy | Behavior |
|----------|----------|
| `manual` (default) | Conflict flagged in UI; user selects which version to keep |
| `local_wins` | Local version overwrites remote |
| `remote_wins` | Remote version overwrites local |
| `merge` | Automatic merge where possible (future) |

### Resolution Flow

```
Conflict detected
    │
    ├── manual:
    │      └── Conflict dialog → User picks local/remote/both
    │
    ├── local_wins:
    │      └── Local changes pushed to Gateway
    │
    ├── remote_wins:
    │      └── Remote changes applied locally
    │
    └── merge:
           └── Automatic three-way merge (future)
```

## Offline Sync Queue

When offline, changes are queued in the `OfflineManager`:

```
User makes change offline
    → Action queued (status: queued)
    → Gateway unavailable → remains queued
    → Reconnect detected
    → SyncManager processes queue
    → Actions replayed in order
    → Queue cleared on success
```

Each queued action records:

- `id` — unique identifier
- `action_type` — e.g. `sync.projects`, `sync.conversations`
- `payload` — JSON-serialized change data
- `queued_at` — timestamp
- `status` — Pending / InFlight / Completed / Failed

## Auto-Sync Configuration

Controlled by `SyncSettings`:

```rust
pub struct SyncSettings {
    pub auto_sync: bool,                  // default: true
    pub sync_interval_seconds: u64,       // default: 300 (5 min)
    pub conflict_resolution: String,      // default: "manual"
}
```

Auto-sync triggers a full sync at the configured interval when:

- The application is online
- Gateway is connected
- Permission to sync is granted (`SyncAccess`)

## Manual Sync Triggers

Users can trigger sync manually via:

1. **Command Palette** — `Ctrl+Shift+S` ("Trigger Sync")
2. **Sync Page** — "Sync Now" button
3. **Status Bar** — Click sync status indicator
4. **Programmatic** — `commands.triggerSync()`

The `trigger_sync` command:

```rust
pub async fn trigger_sync(state: State<'_, SyncManager>) -> Result<SyncStatus, String> {
    state.start_sync();           // Sets all modules to Syncing
    // ... sync logic ...
    state.resolve_conflicts();    // Attempt conflict resolution
    Ok(state.get_status())
}
```

## Workspace Boundary Enforcement

Sync is scoped to the **active workspace**:

- Only data belonging to the current workspace is synced
- Workspace ID is validated before each sync operation
- Cross-workspace data is never mixed or leaked
- Workspace boundaries are enforced in the Rust backend

## Security Policy Respect During Sync

Synchronization respects all active permission policies:

| Policy | Impact on Sync |
|--------|---------------|
| `SyncAccess` permission | Sync operations require this permission to be granted |
| `NetworkAccess` permission | Gateway connectivity requires this permission |
| `SettingsWrite` permission | Syncing settings changes requires this permission |
| Offline mode | When enabled, sync is paused and changes are queued |
| Local processing mode | When enabled, sync is blocked entirely |
