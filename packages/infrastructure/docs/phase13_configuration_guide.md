## Phase 13 Configuration Guide

### Configuration Sources
- Environment (`EnvironmentConfigurationSource`)
- File (`FileConfigurationSource`)
- Combined and validated through `ConfigurationLoader`

### Environment Pattern
- Profile: `JARVIS_INFRASTRUCTURE_PROFILE`
- Adapter fields:
  - `JARVIS_INFRASTRUCTURE_ADAPTER__<id>__PROVIDER`
  - `JARVIS_INFRASTRUCTURE_ADAPTER__<id>__ENABLED`
  - `JARVIS_INFRASTRUCTURE_ADAPTER__<id>__DEPENDENCIES`
  - `JARVIS_INFRASTRUCTURE_ADAPTER__<id>__SETTINGS__<key>`
  - `JARVIS_INFRASTRUCTURE_ADAPTER__<id>__SECRETS`

### File Shape
```json
{
  "profile": "default",
  "adapters": {
    "database.sqlite": {
      "provider": "sqlite",
      "enabled": true,
      "settings": {"path": ":memory:"}
    }
  }
}
```

### Validation
- Adapter `provider` is required.
- `settings` must be a mapping.
- `dependencies` and `secrets` support list/tuple/comma-separated input.
