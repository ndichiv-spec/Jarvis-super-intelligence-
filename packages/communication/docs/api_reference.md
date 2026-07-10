# JARVIS Communication API Reference

## Gateway API Endpoints

All endpoints are prefixed with `/communication`.

### Conversations

| Method | Path                        | Description               |
|--------|-----------------------------|---------------------------|
| GET    | `/communication/conversations` | List conversations     |

**Query Parameters:**
- `user_id` (optional) - Filter by participant

### Messages

| Method | Path                        | Description               |
|--------|-----------------------------|---------------------------|
| GET    | `/communication/messages`   | List messages             |
| POST   | `/communication/messages`   | Send a message            |
| POST   | `/communication/messages/{message_id}/read` | Mark message as read |

**GET Query Parameters:**
- `conversation_id` - Filter by conversation
- `sender` - Filter by sender
- `receiver` - Filter by receiver
- `limit` - Max results (default: 50)

**POST Body (send message):**
```json
{
  "sender": "string",
  "receiver": "string",
  "body": "string",
  "conversation_id": "string (optional)",
  "subject": "string (optional)",
  "channel": "string (default: internal)"
}
```

### Email

| Method | Path                   | Description    |
|--------|------------------------|----------------|
| POST   | `/communication/email` | Send an email  |

**POST Body:**
```json
{
  "to_addresses": ["string"],
  "subject": "string",
  "body_text": "string",
  "sender": "string",
  "body_html": "string (optional)"
}
```

### Notifications

| Method | Path                              | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | `/communication/notify`           | Send a notification            |
| GET    | `/communication/notifications`    | List notifications             |
| POST   | `/communication/notifications/read-all` | Mark all notifications as read |

**GET Query Parameters:**
- `user_id` (required)
- `unread_only` (boolean, default: false)
- `limit` (default: 50)

**POST Body (send notification):**
```json
{
  "title": "string",
  "body": "string",
  "target_user": "string (optional)",
  "level": "info|success|warning|error|critical"
}
```

### Presence

| Method | Path                      | Description      |
|--------|---------------------------|------------------|
| GET    | `/communication/presence` | List all presence |

### Metrics

| Method | Path                      | Description         |
|--------|---------------------------|---------------------|
| GET    | `/communication/metrics`  | Get metrics summary |

### Streams

| Method | Path                     | Description           |
|--------|--------------------------|-----------------------|
| GET    | `/communication/streams` | List active streams   |

### Unread Counts

| Method | Path                             | Description              |
|--------|----------------------------------|--------------------------|
| GET    | `/communication/unread/{user_id}`| Get unread counts        |

## Studio API Endpoints (Communication Workspace)

All endpoints are prefixed with `/studio/communication`.

| Method | Path                                                | Description                     |
|--------|------------------------------------------------------|---------------------------------|
| GET    | `/studio/communication/analytics`                    | Get communication analytics     |
| GET    | `/studio/communication/conversations`                | List workspace conversations    |
| GET    | `/studio/communication/messages`                     | List workspace messages         |
| GET    | `/studio/communication/messages?conversation_id=`    | Filter by conversation          |
| GET    | `/studio/communication/streams`                      | List active streams             |

## Data Models

### CommunicationMessage
```json
{
  "message_id": "uuid",
  "sender": "string",
  "receiver": "string",
  "channel": "internal|ai_conversation|email|push_notification|websocket|system|external",
  "conversation_id": "uuid|null",
  "message_type": "text|command|event|notification|system|error|warning",
  "priority": "low|normal|high|critical",
  "body": "string",
  "subject": "string|null",
  "timestamp": "ISO8601",
  "delivery_status": "pending|sent|delivered|read|failed",
  "read_status": "unread|read|archived"
}
```

### Notification
```json
{
  "notification_id": "uuid",
  "title": "string",
  "body": "string",
  "level": "info|success|warning|error|critical",
  "source": "string",
  "target_user": "string|null",
  "read": false,
  "timestamp": "ISO8601"
}
```

### Presence
```json
{
  "user_id": "string",
  "status": "online|away|busy|offline|do_not_disturb",
  "current_activity": "string",
  "last_seen": "ISO8601|null",
  "connected_clients": 0
}
```
