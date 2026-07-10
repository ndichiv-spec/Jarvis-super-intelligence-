# JARVIS Streaming Protocol

## Overview

The JARVIS Streaming Engine provides real-time, chunk-based streaming for AI responses, agent execution updates, planning progress, and automation workflows.

## Stream Lifecycle

1. **Start**: Client creates a stream with a unique stream_id
2. **Push**: Server pushes data chunks to the stream
3. **Subscribe**: Clients receive chunks in real-time
4. **End**: Stream is terminated with an "end" chunk type

## Chunk Structure

Each `StreamChunk` contains:

```json
{
  "stream_id": "string",
  "sequence": 0,
  "data": "string",
  "chunk_type": "data",
  "timestamp": "ISO8601",
  "metadata": {}
}
```

### Chunk Types

| Type               | Description                    |
|--------------------|--------------------------------|
| `data`             | Regular data chunk             |
| `agent_update`     | Agent execution status update  |
| `planning_progress`| Planning phase progress        |
| `end`              | Stream termination signal      |

## Streaming Patterns

### AI Response Streaming

```
client -> start_stream("ai-response-123")
client -> stream_ai_response("ai-response-123", generator)
  server -> push_chunk("ai-response-123", "I")
  server -> push_chunk("ai-response-123", " think")
  server -> push_chunk("ai-response-123", " therefore")
  server -> push_chunk("ai-response-123", " I am")
  server -> push_chunk("ai-response-123", "", chunk_type="end")
```

### Agent Execution Streaming

```
client -> stream_agent_execution("agent-exec-456", updates)
  server -> push_chunk("agent-exec-456", "Analyzing input...", chunk_type="agent_update")
  server -> push_chunk("agent-exec-456", "Processing data...", chunk_type="agent_update")
  server -> push_chunk("agent-exec-456", "Generating output...", chunk_type="agent_update")
  server -> push_chunk("agent-exec-456", "", chunk_type="end")
```

## Subscribing to Streams

Clients can subscribe to receive chunks as they arrive:

```python
async for chunk in engine.streaming.subscribe(stream_id):
    process_chunk(chunk)
```

## Gateway Integration

Clients access streams through the Gateway API:

```
GET /communication/streams - List active streams
GET /gateway/stream/{path} - SSE streaming proxy
```

## WebSocket Integration

The WebSocket manager broadcasts stream events to connected clients subscribed to the stream topic.
