## Trigger Model

### Supported Trigger Sources
- Manual requests
- Brain decisions
- Agent requests
- Scheduled execution
- Event-driven execution
- External signals (adapter-ready contract)
- User actions

### Trigger Processing
- Triggers are represented as typed `TriggerDefinition` and `TriggerEvent` contracts.
- `InMemoryTriggerEngine` routes events to registered workflows and emits execution requests.
- Trigger handling is decoupled from transport/infrastructure; integrations are adapter responsibilities.
