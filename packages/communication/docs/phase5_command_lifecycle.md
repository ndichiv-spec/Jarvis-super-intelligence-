# Phase 5 — Command Lifecycle

## Flow

1. Caller creates `CommandMessage`.
2. Command enters `CommandBus.dispatch`.
3. Validation and authorization hooks run through `PipelineEngine`.
4. Middleware chain executes around the command handler.
5. Handler returns result or raises an error.
6. Bus emits `CommandResult` with success/value or typed errors.
7. Execution contracts (`before_dispatch` / `after_dispatch`) can observe or enforce policies.

## Guarantees

- Request/response contract through `CommandResult`
- Hook-based enforcement for validation and authorization
- Retry/logging/metrics support through pipeline hooks
