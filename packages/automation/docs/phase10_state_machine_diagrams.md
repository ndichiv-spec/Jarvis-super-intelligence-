## State Machine Diagrams

### Workflow Execution State Machine
```text
created -> queued -> running -> completed
                    |-> failed -> compensating -> failed
                    |-> retrying -> running
                    |-> waiting -> running
                    |-> paused -> running
                    |-> cancelled
completed/failed/cancelled -> archived
```

### Step State Machine
```text
pending -> queued -> running -> completed
                     |-> waiting_approval -> running
                     |-> retrying -> running
                     |-> failed -> compensating -> failed
                     |-> skipped
                     |-> cancelled
```
