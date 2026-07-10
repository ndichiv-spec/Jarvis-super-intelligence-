# Phase 14 Developer Guide

## Local Development

- Package path: `packages/api`
- Main entrypoints:
  - `jarvis_api.gateway.kernel.GatewayKernel`
  - `jarvis_api.gateway.app.create_gateway_app`

## Extension Points

- Register new protocols through `ProtocolRegistry`.
- Register routes via `GatewayKernel.register_route()`.
- Add middleware through `RequestPipeline` / `ResponsePipeline`.
- Attach policy/rate-limit/session/version/observability components via kernel dependency injection.

## Important Constraints

- Keep business logic outside gateway package.
- Keep contracts strictly typed and async-first.
- Preserve protocol-agnostic orchestration in kernel.
