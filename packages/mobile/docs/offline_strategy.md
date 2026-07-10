# Offline Strategy

## Overview

JARVIS Mobile supports offline operation with automatic synchronization when connectivity is restored. The strategy follows a queue-and-sync pattern.

## Offline Queue

The `OfflineQueue` class manages pending actions:

1. **Enqueue**: When connectivity is lost, user actions are serialized and stored in SQLite (`offline_actions` table)
2. **Process**: When connectivity is restored, queued actions are replayed in order
3. **Tracking**: Failed actions are tracked for user visibility

### Offline Action Schema

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | UUID primary key |
| action_type | TEXT | Action identifier (e.g., 'send_message', 'archive_memory') |
| payload | TEXT | JSON-encoded action data |
| created_at | TEXT | ISO 8601 timestamp |
| status | TEXT | 'pending', 'completed', 'failed' |

## Cached Data

### Conversations
- Cached in `conversations` table (SQLite)
- Includes title, workspace, timestamps, message count
- User can browse cached conversations while offline

### Messages
- Cached in `messages` table (SQLite)
- Includes role, content, timestamps
- User can review cached conversation history

### Projects
- Cached in `projects` table (SQLite)
- Includes name, description, status, progress
- User can browse project metadata while offline

### Preferences
- Cached in `preferences` table (SQLite)
- Key-value store for app settings
- Works offline

## Synchronization

### Auto-sync triggers:
1. App comes to foreground
2. Connectivity is restored (via `ConnectivityService`)
3. Periodic background sync (future enhancement)

### Sync flow:
1. Connectivity check via `connectivity_plus`
2. If online, process offline queue
3. Refresh cached data from gateway
4. Update sync status in UI

## Connectivity Awareness

The `ConnectivityService` wraps `connectivity_plus`:
- Monitors network state changes
- `OfflineBanner` widget displays when offline
- Providers check connectivity before making API calls
- Diagnostics page shows current connectivity status
