# Phase 5 — Extension Guide

## Extension Points

- `MessageSerializer` for JSON/MessagePack/Protobuf/binary adapters
- `EventStore` for event persistence/replay/snapshots/versioning adapters
- `Scheduler` for delayed/recurring/cron execution adapters
- `DeadLetterSink` for failed message routing
- Pipeline hooks (`ValidationHook`, `AuthorizationHook`, `LoggingHook`, `RetryHook`, `MetricsHook`)
- `RoutingEngine` route table for custom dispatch strategies

## Adapter Pattern

1. Implement the protocol in your infrastructure package.
2. Inject implementation into communication buses.
3. Keep protocol-facing boundaries in domain/application layers.

## Suggested Packaging

- `packages/infrastructure/.../serialization`
- `packages/infrastructure/.../messaging`
- `packages/infrastructure/.../observability`

## Contract Safety

- Keep message contracts immutable.
- Do not mutate context or payload in adapters.
- Preserve `correlation_id` lineage across process boundaries.
- Emit errors to dead-letter pathways instead of silent drops.
