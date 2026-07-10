## Extension Guide

### Extension Points
- Implement registry, state, trigger, scheduler, monitoring, and policy adapters behind existing contracts.
- Keep adapter concerns outside `jarvis_automation` domain orchestration logic.

### Adapter Principles
- Respect typed domain models without leaking transport/storage specifics.
- Map external events/schedules into `TriggerEvent` and scheduler contracts.
- Surface execution telemetry into monitoring contracts with consistent identifiers.
