# Phase 14 Gateway Architecture

## Purpose

The Professional Service Gateway Platform is the unified, protocol-aware entry point for the JARVIS Ecosystem.

The gateway is responsible for request validation, authorization integration, routing, pipeline processing, streaming orchestration, and response normalization.

## Core Components

1. `GatewayKernel`
   - Central coordinator for request handling.
   - Delegates all domain execution to subsystem handlers.
2. `ProtocolRegistry`
   - Maintains protocol descriptors and capabilities.
   - Supports REST, WebSocket, SSE, MCP, and future protocols.
3. `RoutingEngine`
   - Maps inbound paths to subsystem routes.
   - Uses deterministic longest-prefix route resolution.
4. `RequestPipeline` and `ResponsePipeline`
   - Middleware execution chain for cross-cutting concerns.
5. `StreamingEngine`
   - Wraps stream payloads into sequence-aware envelopes.
6. `SessionManager`
   - Tracks session identity, workspace, protocol metadata, and lifecycle.
7. `ApiVersionManager`
   - Implements semantic version registration and compatibility/deprecation resolution.
8. `RateLimiter`
   - Applies per-scope policies (user/workspace/org/extension/protocol).
9. `GatewayPolicyEngine`
   - Enforces enterprise governance and protocol/workspace/version rules.
10. `ApiMetadataRegistry`
    - Stores endpoint/service metadata contracts.
11. `InMemoryObservability`
    - Structured logs, counters, latency recording, health, and stats.

## Architecture Rules

- No business logic in gateway modules.
- No subsystem memory/knowledge/agent/tool/automation execution logic in gateway modules.
- The kernel only orchestrates and delegates.
- Protocol extensibility is achieved by registration, not kernel rewrites.

## ASGI and FastAPI Layer

- `create_gateway_app()` exposes:
  - `/health`
  - `/stats`
  - `/gateway/stream/{path}` for SSE-oriented requests
  - `/gateway/{path}` for REST-oriented requests
  - `/gateway/ws/{path}` for WebSocket sessions

## Validation Scope

All implementation and tests for Phase 14 are confined to `packages/api`.
