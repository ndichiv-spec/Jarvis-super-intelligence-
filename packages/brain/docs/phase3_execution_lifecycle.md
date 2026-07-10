### Phase 3 Execution Lifecycle

### Workflow States

- `queued`
- `running`
- `paused`
- `cancelled`
- `completed`
- `failed`
- `retry`
- `rollback`

### State Transition Rules

- `queued` -> `running` or `cancelled`
- `running` -> `paused`, `failed`, `completed`, or `cancelled`
- `paused` -> `running` or `cancelled`
- `failed` -> `retry` or `rollback`
- `retry` -> `running` or `cancelled`
- `rollback` -> `completed` or `failed`

### Immutable State Tracking

Each transition updates immutable `BrainExecutionState` with:

- execution id and trace id
- created/updated timestamps
- current workflow status
- current stage and completed stages
- errors and warnings
- metrics counters
- execution history timeline entries
