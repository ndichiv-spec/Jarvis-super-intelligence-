# Phase 14 Protocol Model

## Registered Protocols

| Protocol | Transport | Streaming | Status |
|---|---|---|---|
| REST | HTTP | No (default) | Enabled |
| WebSocket | WS | Yes | Enabled |
| SSE | HTTP | Yes | Enabled |
| MCP | HTTP | Yes | Enabled |
| gRPC | HTTP/2 | Yes | Prepared (disabled by default) |
| GraphQL | HTTP | Yes | Prepared (disabled by default) |

## Extensibility Contract

- New protocols are introduced through `ProtocolRegistry.register()`.
- Kernel logic is protocol-agnostic and consumes descriptors only.
- Policy and routing decisions can use protocol metadata without code branching in core orchestration.

## Protocol Responsibilities

- REST: synchronous request/response.
- WebSocket: interactive bidirectional sessions.
- SSE: server-initiated stream delivery.
- MCP: extension/tool context exchange and event streaming.
