# Phase 14 Integration Guide

## Integrating a Subsystem

1. Register a route for subsystem path prefix.
2. Provide route executor implementation that delegates to subsystem service.
3. Optionally register API metadata and additional middleware.

## Integrating a New Protocol

1. Register `ProtocolDescriptor` in `ProtocolRegistry`.
2. Add endpoint adapter in `create_gateway_app()` if transport-specific ingress is needed.
3. Reuse existing kernel flow (validation, auth, policy, routing, normalization).

## Integration Validation

- Verify request reaches expected route.
- Verify standardized envelope output.
- Verify observability counters and latency metrics are populated.
- Verify policy/rate-limit contracts for the new integration.
