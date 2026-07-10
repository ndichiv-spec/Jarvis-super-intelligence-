# Phase 5 — Query Lifecycle

## Flow

1. Caller creates `QueryMessage` with optional filters/pagination.
2. Query enters `QueryBus.dispatch`.
3. Effective filters and pagination are computed from message + execution options.
4. Optional cache hook lookup runs before execution.
5. Validation/authorization/middleware pipeline executes around query handler.
6. Optional projection contract transforms raw data.
7. Optional cache hook stores transformed result.
8. `QueryResult` returns data, cache status, filters, pagination, and typed errors.

## Guarantees

- Read-oriented contract with explicit filtering/pagination metadata
- Optional cache and projection extension points
- Strongly typed query response envelope
