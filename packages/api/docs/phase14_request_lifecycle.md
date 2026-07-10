# Phase 14 Request Lifecycle

1. Client request enters gateway endpoint (`REST`, `SSE`, or `WebSocket`).
2. `GatewayRequest` contract is created with identity/workspace/protocol metadata.
3. `ProtocolRegistry` validates protocol support and enablement.
4. `ApiVersionManager` resolves semantic version compatibility.
5. `RoutingEngine` resolves subsystem route.
6. `RequestValidator` and request middleware pipeline execute.
7. Authorization integration executes for route and request context.
8. Rate-limit policies are evaluated.
9. Governance policies are enforced.
10. Session is opened/touched and lifecycle metadata is updated.
11. Route execution is delegated externally (business logic remains out of gateway).

## Failure Path

- Any failure is transformed into standardized `GatewayErrorContract` output.
- Kernel emits observability counters and latency metrics in all paths.
