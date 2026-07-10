## Execution Model

### Orchestration Principles
- The workflow engine is async-first and coordinates typed steps through execution context and state transitions.
- Automation orchestrates tools/agents through metadata and contracts; step business execution remains decoupled.

### Supported Control Flow
- Sequential execution via ordered step list.
- Parallel execution via `StepType.PARALLEL` and grouped `sub_steps`.
- Conditional and loop-capable steps via typed `StepType.CONDITION` and `StepType.LOOP` contracts.
- Sub-workflow and nested workflows via `StepType.SUB_WORKFLOW` and reusable workflow definitions.

### Execution Identity
- Each run carries `workflow_id`, `execution_id`, `correlation_id`, workspace/project context, step pointer, and history trail.
