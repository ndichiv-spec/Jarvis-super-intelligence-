## Developer Guide

### Getting Started
- Add workflows by creating `WorkflowDefinition` instances with typed steps and contracts.
- Register workflows through `AutomationKernel.register_workflow` or template registration.

### Running Tests
- Execute: `uv run pytest packages\\automation\\tests -q`

### Design Rules
- Keep implementations async-first and strongly typed.
- Depend on contracts/protocols, not infrastructure.
- Preserve framework and scheduler independence.
