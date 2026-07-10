# Synchronization Guide

## Architecture

All synchronization flows through the Professional Service Gateway. The mobile app never communicates with backend services directly.

## Gateway Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/gateway/brain/conversations` | List conversations |
| POST | `/gateway/brain/conversations` | Create conversation |
| POST | `/gateway/brain/conversations/{id}/messages` | Send message |
| GET | `/gateway/brain/projects` | List projects |
| GET | `/gateway/memory/items` | List memories |
| GET | `/gateway/knowledge/search` | Search knowledge |
| GET | `/gateway/automation/workflows` | List workflows |
| GET | `/gateway/notifications` | List notifications |

## Streaming

- SSE at `/gateway/stream/brain/conversations/stream/{id}` for real-time conversation streaming
- WebSocket at `/gateway/ws/...` for bidirectional communication (future)
- The `SseClient` class handles SSE parsing

## Response Format

All gateway responses follow the standard envelope:

```json
{
  "ok": true,
  "data": { ... },
  "error": { "code": "...", "message": "..." },
  "metadata": { "request_id": "...", "session_id": "..." }
}
```

## Authentication Headers

All requests include:
- `x-api-version`: API version
- `x-subject-id`: User identity
- `x-session-id`: Current session token
- `x-workspace-id`: Active workspace

## Offline Sync Process

1. User performs action while offline
2. Action is queued in local SQLite database
3. `ConnectivityService` detects restored connectivity
4. `OfflineQueue.processQueue()` replays queued actions
5. Successful actions are marked 'completed'
6. Failed actions are marked 'failed' with error details
7. Diagnostics page shows pending/failed counts
