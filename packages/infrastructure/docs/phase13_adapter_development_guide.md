## Phase 13 Adapter Development Guide

### Adapter Checklist
- Define immutable `AdapterMetadata`.
- Declare explicit `dependencies`.
- Implement `configure`, `start`, `stop`, and `health`.
- Keep provider-specific details encapsulated in the adapter.

### Client Injection Pattern
- Model external dependencies as protocol-typed clients.
- Validate required clients during `start()`.
- Keep adapter logic testable using fake clients.

### Configuration Pattern
- Read adapter-specific settings from `AdapterConfiguration.settings`.
- Use secret references instead of embedding credentials in code.

### Validation Pattern
- Unit-test adapter behavior in isolation.
- Add kernel-level integration test coverage for dependency order and status transitions.
