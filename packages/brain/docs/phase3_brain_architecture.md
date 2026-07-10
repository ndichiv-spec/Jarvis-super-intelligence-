### Phase 3 Brain Architecture

The Brain package (`packages/brain`) implements the permanent orchestration architecture for JARVIS.

### Bounded Architecture Layers

- **Contracts and models:** `jarvis_brain.models`, `jarvis_brain.interfaces`
- **Execution engines:** request/context/intent/planning/reasoning/decision/workflow/tool/agent/response modules
- **Orchestration kernel:** `jarvis_brain.kernel.BrainKernel`
- **Observability contracts:** `jarvis_brain.observability` + protocol interfaces

### Design Decisions

- Components communicate only through explicit protocol contracts.
- Execution state is immutable and updated via dataclass replacement.
- Reasoning is deterministic/rule-based and does not depend on language models.
- Tool and agent modules coordinate contracts only; they do not execute external workloads.
- Architecture is framework-independent (no HTTP, ORM, database, AI SDK dependencies).

### Core Components

1. Request Processor: normalizes input, initializes execution and trace IDs.
2. Context Engine: merges conversation/user/memory/knowledge/workspace/project/system/device context.
3. Intent Engine: classifies intent, ambiguity, and capabilities.
4. Planning Engine: generates ordered executable tasks and strategy.
5. Reasoning Engine: evaluates risks/conflicts and task priorities.
6. Decision Engine: chooses final execution action.
7. Workflow Engine: controls lifecycle transitions and immutable state history.
8. Tool Coordinator: validates tool contract availability and permissions.
9. Agent Coordinator: builds specialist-agent delegation contracts.
10. Response Composer: produces structured `BrainResponse` payload.
11. Brain Kernel: orchestrates full lifecycle and observability integration.
