## Workflow Lifecycle

### Lifecycle States
- `created` -> `queued` -> `running` -> terminal states (`completed`, `failed`, `cancelled`) with optional `retrying`, `compensating`, `archived` transitions.
- Intermediate states include `waiting` and `paused` for approval/synchronization and operator control.

### Lifecycle Responsibilities
- `AutomationKernel` receives registration and execution requests.
- `InMemoryWorkflowEngine` orchestrates step progression.
- `InMemoryStateManager` stores state transitions and execution snapshots.
- `InMemoryMonitoringEngine` records duration, success/failure, and health metrics.

### Recovery Semantics
- Retry policies may re-enter `retrying` then return to `running`.
- Compensation policies transition failed paths into `compensating` before finalization.
- Paused executions can return to `running` through explicit resume actions.
