## Phase 10 Automation Architecture

### Purpose
- `jarvis_automation` provides the Professional Automation Platform as a framework-independent orchestration subsystem.
- The package coordinates workflow execution; it does not execute infrastructure-bound side effects directly.

### Core Components
- `kernel.py`: `AutomationKernel` composition root and lifecycle coordinator.
- `registry.py`: in-memory workflow registration and metadata index.
- `models.py`: strongly typed domain contracts (workflow, steps, retries, compensation, approvals, triggers, policies, states).
- `engine.py`: workflow orchestration engine for sequencing, branching, parallel and nested execution patterns.
- `triggers.py`: trigger routing and dispatch contracts.
- `scheduler.py`: scheduling contracts for one-time, recurring, cron, calendar, delay, and interval modes.
- `state.py`: execution state machine persistence contract + in-memory implementation.
- `retry.py`: retry policy and backoff handling.
- `compensation.py`: compensation orchestration and rollback contracts.
- `approval.py`: approval gate management.
- `variables.py`: scoped variable storage and mutation controls.
- `context.py`: execution context identity and history model.
- `monitoring.py`: execution telemetry and health aggregation.
- `policies.py`: governance and execution policy evaluation.
- `templates.py`: structural workflow template catalog.

### Dependency Boundaries
- No direct dependencies on `FastAPI`, databases, queues, operating-system schedulers, or external workflow engines.
- Infrastructure integrations are deferred to future adapter packages via protocols and dependency inversion.
