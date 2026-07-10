### Phase 3 Execution Pipeline

Every request in the Brain kernel follows the same deterministic pipeline:

1. `REQUEST_PROCESSED`
2. `CONTEXT_BUILT`
3. `INTENT_DETERMINED`
4. `PLAN_GENERATED`
5. `PLAN_EVALUATED`
6. `DECISION_MADE`
7. `TOOLS_COORDINATED`
8. `AGENTS_COORDINATED`
9. `RESPONSE_COMPOSED`

### Pipeline Guarantees

- Full stage tracking for every execution.
- Immutable execution state snapshots with timeline history.
- Structured error capture and failed-state transitions.
- Deterministic decisioning independent of model providers.

### Strategy Support

- Sequential plans
- Parallel plans
- Hybrid plans

Strategy selection originates in planning and is re-evaluated by reasoning before decision.
