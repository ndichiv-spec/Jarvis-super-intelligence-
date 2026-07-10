## Phase 13 Adapter Model

### Adapter Contract Shape
- `adapter_metadata`: stable runtime metadata for registration and reporting.
- `dependencies`: other adapter identifiers required before startup.
- Lifecycle methods:
  - `configure(configuration)`
  - `start()`
  - `stop()`
  - `health()`

### Metadata Fields
- `identifier`
- `version`
- `provider`
- `capabilities`
- `configuration_profile`
- `compatibility`
- `status`

### Health Model
- `availability`
- `connectivity`
- `latency_ms`
- `version`
- `compatibility`
- `failures`
- `recovery_status`
- `checked_at`

### Extension Pattern
- Add a new adapter class under `jarvis_infrastructure.adapters`.
- Reuse `BaseInfrastructureAdapter` for consistent lifecycle behavior.
- Keep provider/client details isolated behind protocol-typed dependencies.
