# Configuration

Configuration is managed by `ConfigurationLoader` (`app/configuration.py`) using a layered resolution system. Each config value tracks its origin source for traceability.

## Layering (Priority: Last Wins)

```
 1. System defaults (lowest priority)
            │
            ▼
 2. .env file
            │
            ▼
 3. Profile JSON (profiles/{profile}.json)
            │
            ▼
 4. JARVIS_* environment variables (highest priority)
```

### Layer Details

**1. Defaults** — hardcoded in `ConfigurationLoader.load_defaults()`:

| Key | Default |
|---|---|
| `app.debug` | `False` |
| `app.log_level` | `info` |
| `app.profile` | `development` |
| `app.gateway_port` | `8000` |
| `app.home_url` | `http://localhost:3000` |
| `app.gateway_host` | `0.0.0.0` |
| `app.data_dir` | `data` |
| `app.database_url` | `sqlite:///data/jarvis.db` |
| `app.redis_url` | `""` (empty) |
| `app.qdrant_url` | `http://localhost:6333` |
| `app.secret_key` | `change-me-in-production` (secret) |

**2. `.env` file** — loaded from `{root}/.env`. Lines are parsed:

```env
APP_DEBUG=true
APP_LOG_LEVEL=debug
APP_SECRET_KEY=my-secret
APP_REDIS_URL=redis://localhost:6379
```

Keys are lowercased and underscores replaced with dots (e.g., `APP_DEBUG` → `app.debug`).

**3. Profile JSON** — loaded from `{root}/profiles/{profile}.json`. The profile name comes from the `JARVIS_PROFILE` env var or defaults to `development`.

```json
{
  "config": {
    "app.debug": { "value": true, "secret": false },
    "app.database_url": { "value": "postgresql://...", "secret": true }
  }
}
```

**4. Environment variables** — any `JARVIS_*` variable. Double underscores map to dots (e.g., `JARVIS_APP__DEBUG` → `app.debug`). Values are auto-parsed: `"true"`/`"false"` → bool, numeric strings → int/float.

```bash
export JARVIS_APP__DEBUG=true
export JARVIS_APP__SECRET_KEY="production-key-here"
```

## AppConfig Fields

The resolved configuration is returned as an immutable `AppConfig` frozen dataclass:

| Field | Type | Default | Description |
|---|---|---|---|
| `debug` | `bool` | `False` | Enable debug mode |
| `log_level` | `str` | `"info"` | Logging level (debug, info, warning, error) |
| `log_file` | `str` | `""` | File path for log output (empty = console only) |
| `profile` | `str` | `"development"` | Active configuration profile name |
| `home_url` | `str` | `"http://localhost:3000"` | Frontend home URL |
| `gateway_host` | `str` | `"0.0.0.0"` | Gateway bind address |
| `gateway_port` | `int` | `8000` | Gateway listen port |
| `data_dir` | `str` | `"data"` | Data storage directory |
| `plugins_dir` | `str` | `"plugins"` | Plugins directory |
| `config_dir` | `str` | `"config"` | Config directory |
| `database_url` | `str` | `"sqlite:///data/jarvis.db"` | Database connection URL |
| `redis_url` | `str` | `""` | Redis connection URL (optional) |
| `qdrant_url` | `str` | `"http://localhost:6333"` | Qdrant vector DB URL |
| `secret_key` | `str` | `"change-me-in-production"` | Secret key for crypto/signing |
| `extra` | `dict[str, Any]` | `{}` | Arbitrary extra config from `app.extra.*` keys |

## Validation

`ConfigurationLoader.validate()` checks for required keys:

```python
loader.validate()  # → list[str] of issues
```

Required keys: `app.debug`, `app.log_level`, `app.profile`, `app.database_url`.

## Runtime Usage

Access config through the `Runtime` facade:

```python
runtime = Runtime()
runtime.start()

runtime.config.debug        # → bool
runtime.config.profile      # → "development"
runtime.config.database_url # → "sqlite:///data/jarvis.db"
runtime.config.extra        # → {"version": "2.0.0", ...}
```

## ConfigEntry Tracking

Each resolved value is stored as a `ConfigEntry`:

```python
@dataclass(frozen=True)
class ConfigEntry:
    key: str
    value: Any
    source: str       # "default" | ".env" | "profile:production" | "environment"
    secret: bool      # True for sensitive values
```

## Security Notes

- The default `secret_key` value `"change-me-in-production"` triggers warnings in `EnvironmentValidator` and `Diagnostics`.
- Keys containing `SECRET`, `KEY`, `TOKEN`, or `PASSWORD` in env var names are automatically marked as secrets.
- The `config` CLI command masks the secret key: it only reports whether it is set (non-default).
