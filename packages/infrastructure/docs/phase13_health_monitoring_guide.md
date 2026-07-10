## Phase 13 Health Monitoring Guide

### Health Dimensions
- Availability
- Connectivity
- Latency
- Compatibility
- Failure count
- Recovery status

### Runtime Flow
- Each adapter reports health via `health()`.
- `InfrastructureKernel` stores results through `AdapterHealthMonitor`.
- `metadata_snapshot()` and `health_snapshot()` provide operational visibility.

### Failure and Recovery
- On startup/runtime exception, the kernel marks adapter status as `FAILED`.
- Health monitor increments failure counters via `mark_failure`.
- Recovery status transitions from `RECOVERING` to `FAILED` when failures accumulate.
