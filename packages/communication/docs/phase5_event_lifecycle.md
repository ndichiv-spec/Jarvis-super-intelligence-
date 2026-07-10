# Phase 5 — Event Lifecycle

## Flow

1. Producer creates `EventMessage` with immutable payload and optional `ExecutionContext`.
2. Producer publishes through `EventBus.publish` or `MessageBus.publish_event`.
3. Event bus resolves matching subscriptions by event name, filter predicates, and priority.
4. Handlers execute in priority order.
5. One-time subscriptions are removed after first execution.
6. Handler failures are routed to the dead-letter contract when configured.
7. Historical events can be replayed through `EventBus.replay` and replay providers.

## Guarantees

- Deterministic priority ordering
- Subscription-level filtering
- Explicit replay contract
- Dead-letter extension point for failed deliveries
