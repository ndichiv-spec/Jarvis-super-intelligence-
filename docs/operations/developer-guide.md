# Developer Guide

## Environment Setup

### Prerequisites

- Python ≥ 3.13
- `uv` package manager (see [docs](https://docs.astral.sh/uv/))

### Clone and Install

```bash
git clone <repo-url>
cd Jarvis
uv sync
```

Activate the virtual environment (created by `uv sync` at `.venv/`):

```powershell
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
```

### Lint & Type Check

```bash
ruff check .                      # Linting
mypy app/                         # Static type checking
black --check app/                # Formatting check
```

Configuration is in `pyproject.toml`:

- Ruff: line length 100, target Python 3.13
- MyPy: strict mode
- Black: line length 100

## Running Tests

```bash
uv run pytest                          # All tests
uv run pytest tests/app/test_lifecycle.py -v   # Single file
uv run pytest -k "test_valid"          # Keyword match
uv run pytest --cov=app                # With coverage
```

Test configuration (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-config", "--strict-markers"]
```

### Test File Structure

```
tests/
├── test_workspace.py
└── app/
    ├── test_lifecycle.py       # LifecycleManager state machine
    ├── test_kernel.py          # AppKernel orchestration
    ├── test_registry.py        # ServiceRegistry & dependency graph
    ├── test_health.py          # HealthMonitor aggregation
    ├── test_configuration.py   # ConfigurationLoader layering
    ├── test_environment.py     # EnvironmentValidator checks
    ├── test_diagnostics.py     # DiagnosticReport generation
    ├── test_startup.py         # run_startup sequence
    ├── test_runtime.py         # Runtime facade
    ├── test_cli.py             # CLI command dispatch
    └── test_modules.py         # Module-level smoke tests
```

## Running the Platform

```bash
uv run python -m jarvis start
uv run python -m jarvis start --config /path/to/root
uv run python -m jarvis stop
uv run python -m jarvis status
uv run python -m jarvis health
uv run python -m jarvis doctor
uv run python -m jarvis test
```

## Adding New Services

1. **Define the service handle** — create a `ServiceHandle` with unique ID, name, dependencies, and capabilities:

   ```python
   from app.registry import ServiceHandle

   new_service = ServiceHandle(
       id="my-service",
       name="My Service",
       version="1.0.0",
       dependencies=("security",),
       capabilities=("my-capability",),
   )
   ```

2. **Register in the kernel** — add to the `_register_platform_services()` method in `app/kernel.py`:

   ```python
   platform_services: list[ServiceHandle] = [
       # ... existing services ...
       ServiceHandle(id="my-service", name="My Service", version="1.0.0",
                     dependencies=("security",), capabilities=("my-capability",)),
   ]
   ```

3. **Health reporting** — the kernel automatically registers health checks for new services. Status updates happen during `run_startup()`.

4. **Update startups** — if the service has startup initialization logic, extend `run_startup()` in `app/startup.py` to perform any service-specific setup during Phase 4.

## Extending Configuration

1. **Add a field to AppConfig** — in `app/configuration.py`:

   ```python
   @dataclass(frozen=True)
   class AppConfig:
       # ... existing fields ...
       my_setting: str = "default-value"
   ```

2. **Add a default entry** — in `ConfigurationLoader.load_defaults()`:

   ```python
   self._entries["app.my_setting"] = ConfigEntry(
       key="app.my_setting", value="default-value", source="default"
   )
   ```

3. **Wire into resolve** — in `ConfigurationLoader.resolve()`:

   ```python
   self._resolved = AppConfig(
       # ... existing mappings ...
       my_setting=self._str("app.my_setting"),
   )
   ```

4. **Override via env** — set `JARVIS_APP__MY_SETTING=production-value`.

5. **Expose in CLI** — add to `cmd_config` in `app/cli/commands/config.py`:

   ```python
   output = {
       # ... existing fields ...
       "my_setting": runtime.config.my_setting,
   }
   ```

## Creating CLI Commands

1. **Create the command module** — `app/cli/commands/<name>.py`:

   ```python
   """<NAME> command — description."""

   from __future__ import annotations
   import argparse
   from app.runtime import Runtime

   def cmd_<name>(args: argparse.Namespace, runtime: Runtime) -> int:
       # Your command logic here
       print("Hello from <name>")
       return 0
   ```

2. **Register the subparser** — in `app/cli/__init__.py`:

   ```python
   p_<name> = sub.add_parser("<name>", help="Description")
   p_<name>.add_argument(...)  # if needed
   ```

3. **Map the command** — in `_COMMAND_MAP`:

   ```python
   _COMMAND_MAP: dict[str, str] = {
       # ... existing commands ...
       "<name>": "app.cli.commands.<name>",
   }
   ```

## Troubleshooting

### Common Issues

| Symptom | Likely Cause | Check |
|---|---|---|
| `LifecycleError: Cannot transition from created to ready` | Skipped intermediate states | Use `initialize()` then `mark_ready()` |
| `StartupError: Environment validation failed` | Python < 3.13 or missing config | Run `python --version`, check config path |
| `ValueError: Service 'X' already registered` | Duplicate service ID in `_register_platform_services()` | Use unique IDs |
| `ValueError: Circular dependency detected` | Dependency cycle in service graph | Check `dependencies` tuples for cycles |
| Default secret key warning | `secret_key` not overridden in production | Set `JARVIS_APP__SECRET_KEY` env var |
| Config not taking effect | Wrong layer priority | Environment vars override profile, which overrides `.env` |

### Debug Logging

```bash
export JARVIS_APP__LOG_LEVEL=debug
uv run python -m jarvis start
```

### Diagnostic Output

```bash
uv run python -m jarvis doctor
```

Displays full platform state: lifecycle, services, health, configuration summary, dependency graph, and warnings.
