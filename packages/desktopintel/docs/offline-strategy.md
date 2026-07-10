# Offline Strategy

## Offline Architecture Overview

```
┌───────────────────────────────────────┐
│            Online Mode                │
│  Gateway Connected ↔ Live Sync        │
└─────────────────┬─────────────────────┘
                  │ User toggle / network loss
                  ▼
┌───────────────────────────────────────┐
│            Offline Mode               │
│                                       │
│  ┌──────────────────────┐             │
│  │   Local Cache        │             │
│  │   ├─ Conversations   │             │
│  │   └─ Knowledge       │             │
│  └──────────────────────┘             │
│                                       │
│  ┌──────────────────────┐             │
│  │   Action Queue       │             │
│  │   ├─ Pending ops     │             │
│  │   ├─ InFlight ops    │             │
│  │   ├─ Completed ops   │             │
│  │   └─ Failed ops      │             │
│  └──────────────────────┘             │
└─────────────────┬─────────────────────┘
                  │ Reconnect detected
                  ▼
┌───────────────────────────────────────┐
│         Sync Resume                   │
│  Flush queue → Resolve conflicts      │
│  → Return to online                   │
└───────────────────────────────────────┘
```

The `OfflineManager` (`src-tauri/src/offline/mod.rs`) manages three data stores when the application is offline:

## Caching Strategy for Conversations

Conversations are cached locally for offline reading and reference:

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique conversation ID |
| `title` | String | Conversation title |
| `cached_at` | String | When this conversation was cached |
| `message_count` | u64 | Number of messages in the conversation |

- **Cache trigger**: Conversations are cached when viewed while online (auto-cache enabled by default via `OfflineSettings::auto_cache_recent`)
- **Capacity**: Default max 50 conversations (`OfflineSettings::max_cached_conversations`)
- **Eviction**: Least recently accessed conversations are evicted when the limit is reached
- **User control**: Users can pin specific conversations to prevent eviction

## Caching Strategy for Knowledge

Knowledge items are cached subject to policy and storage limits:

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique knowledge item ID |
| `title` | String | Knowledge item title |
| `source` | String | Source collection or workspace |
| `cached_at` | String | When this item was cached |
| `size_bytes` | u64 | Storage size of the item |

- **Cache trigger**: Knowledge items accessed during online sessions are cached
- **Capacity**: Default max 200 items (`OfflineSettings::max_cached_knowledge_items`)
- **Policy respect**: Knowledge caching respects knowledge-level access policies; restricted knowledge is never cached
- **Eviction**: LRU eviction when cache is full

## Action Queue for Pending Operations

When the user performs actions offline, they are queued rather than rejected:

```rust
pub enum QueuedActionStatus {
    Pending,    // Waiting to be sent
    InFlight,   // Being sent (during reconnect)
    Completed,  // Successfully synced
    Failed(String), // Permanent failure
}
```

Each queued action contains:

- `id` — unique identifier
- `action_type` — e.g. `sync.projects`, `sync.conversations`, `file.save`
- `payload` — JSON-serialized operation data
- `queued_at` — timestamp of when the action was queued
- `status` — current processing status

Actions are replayed in FIFO order when connectivity is restored.

## Sync Resume on Reconnect

The `resume_sync()` method handles the transition from offline to online:

```
1. Network reestablished
2. User toggles offline mode off
3. OfflineManager::resume_sync() called
4. All queued Pending actions marked Completed
5. All queued InFlight actions marked Failed
6. SyncManager processes any remaining changes
7. Status updated: offline → online synced
```

## Conflict Detection and Resolution

Conflicts between offline changes and remote changes are detected during sync resume:

| Scenario | Detection | Resolution |
|----------|-----------|------------|
| Same item edited offline and online | Timestamp/hash comparison | Manual resolution dialog (default) or auto-strategy |
| Item deleted online, edited offline | Item not found on remote | User notified, local change discarded or re-created |
| Item deleted offline, edited online | Conflict marker | User chooses to keep remote or apply deletion |

See [Synchronization Guide → Conflict Resolution](./synchronization-guide.md#conflict-resolution) for detailed strategies.

## Storage Limits and Management

| Setting | Default | Description |
|---------|---------|-------------|
| `max_cached_conversations` | 50 | Maximum conversations stored locally |
| `max_cached_knowledge_items` | 200 | Maximum knowledge items stored locally |
| `auto_cache_recent` | true | Automatically cache recently accessed items |

The offline status page displays:

- Current storage used (bytes)
- Cached conversation count
- Cached knowledge count
- Queued action count
- Last sync timestamp

## Offline Capabilities vs Online-Only Features

| Feature | Offline | Online Only |
|---------|---------|-------------|
| View cached conversations | ✅ | — |
| View cached knowledge | ✅ | — |
| Compose messages | ✅ (queued) | — |
| Access settings | ✅ (cached) | — |
| View file operations | ✅ (local log) | — |
| **Live Gateway AI queries** | — | ✅ |
| **Real-time sync** | — | ✅ |
| **Integration execution** | — | ✅ |
| **Update checks** | — | ✅ |
| **Dashboard live data** | — | ✅ |

## User Experience Considerations

### Entering Offline Mode

- User can manually toggle offline mode via the Command Palette (`Ctrl+Shift+O`) or Offline page
- Automatic offline detection (future: network status change events)
- Clear visual indicator in the status bar when offline
- Toast notification on transition

### While Offline

- Disabled UI elements for online-only features
- "Pending" badges on components that have queued actions
- Offline status dashboard shows cache and queue stats
- Non-disruptive — all navigation and cached content works normally

### Exiting Offline Mode

- Automatic sync resume when connectivity returns (if `autoSyncOnReconnect` is enabled)
- Progress indicator during queue flush
- Conflict resolution dialogs when needed
- Summary notification: "N changes synced, M conflicts resolved"
