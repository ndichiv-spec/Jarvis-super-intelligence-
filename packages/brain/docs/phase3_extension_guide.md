### Phase 3 Brain Extension Guide

### Add a New Engine Implementation

1. Implement the relevant protocol from `jarvis_brain.interfaces`.
2. Keep implementation framework-independent.
3. Use immutable model contracts from `jarvis_brain.models`.
4. Inject the component into `BrainKernel` constructor.
5. Add/extend unit tests in `packages/brain/tests`.

### Add New Tool Coordination Contracts

1. Extend `RuleBasedToolCoordinator` catalog with a `ToolDefinition`.
2. Define required permissions and purpose.
3. Preserve non-execution behavior (contracts only).
4. Add tests for permission and availability behavior.

### Add New Agent Types

1. Add `AgentDefinition` in `RuleBasedAgentCoordinator` catalog.
2. Extend selection heuristics in `prepare_agents`.
3. Validate availability via coordinator input map.
4. Add tests for routing/selection behavior.

### Add New Decision Strategies

1. Extend `IntentKind`, `Capability`, and `DecisionAction` when needed.
2. Update intent/planning/reasoning/decision engines coherently.
3. Add lifecycle and kernel tests covering new path.
