# Phase 14 Streaming Guide

## Supported Streaming Modes

- Token streaming
- Workflow progress updates
- Agent event feeds
- Automation progress events
- Notifications
- Live telemetry updates

## Streaming Flow

1. Upstream executor returns `GatewayResponse(stream=...)`.
2. `StreamingEngine` wraps each chunk into `StreamEnvelope` with sequence and timestamp.
3. Protocol endpoint formats output:
   - SSE: `data: <json>\n\n`
   - WebSocket: JSON event frames
4. Gateway emits observability metrics for stream requests.

## Contracts

- Ordered sequence numbers per channel.
- Channel identifier based on request id.
- Metadata supports route/subsystem context.
- Policy engine can restrict streaming by protocol.
