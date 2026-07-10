## Phase 13 Developer Guide

### Where to Implement
- Package: `packages/infrastructure/src/jarvis_infrastructure`
- Adapter modules: `adapters/*.py`

### Development Principles
- Keep interfaces/protocol boundaries explicit.
- Avoid vendor leakage beyond adapter modules.
- Prefer protocol-injected clients for external systems.

### Typical Kernel Wiring
- Instantiate adapters.
- Register with `InfrastructureKernel`.
- Load configuration via `ConfigurationLoader`.
- Call `start()`, then inspect metadata/health snapshots.

### Testing Guidance
- Add/extend tests under `packages/infrastructure/tests`.
- Cover happy path, validation failures, and authorization/health edge cases.
