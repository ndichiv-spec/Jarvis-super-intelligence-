# CLI Commands

The JARVIS CLI is dispatched by `app/cli/__init__.py`. All commands follow the pattern `uv run python -m jarvis <command> [options]`.

## Command Reference

| Command | Module | Description |
|---|---|---|
| `start` | `app.cli.commands.start` | Bootstrap and start the platform |
| `stop` | `app.cli.commands.stop` | Graceful platform shutdown |
| `restart` | `app.cli.commands.restart` | Stop then start the platform |
| `status` | `app.cli.commands.status` | Show platform and service status |
| `health` | `app.cli.commands.health` | Show consolidated health report |
| `version` | `app.cli.commands.version` | Display platform version |
| `config` | `app.cli.commands.config` | Display current configuration |
| `logs` | `app.cli.commands.logs` | Tail or inspect platform logs |
| `doctor` | `app.cli.commands.doctor` | Comprehensive diagnostics |
| `test` | `app.cli.commands.test` | Run platform self-test |

## Usage

### start

```bash
uv run python -m jarvis start
uv run python -m jarvis start --config /path/to/config
```

Bootstraps the platform: loads configuration, validates environment, initializes kernel, starts services in dependency order, and prints the banner.

### stop

```bash
uv run python -m jarvis stop
```

Gracefully shuts down the platform. Services are stopped in reverse startup order.

### restart

```bash
uv run python -m jarvis restart
uv run python -m jarvis restart --config /path/to/config
```

Stops and then restarts the platform. Prints the new status and service count after restart.

### status

```bash
uv run python -m jarvis status
```

Output:

```
Status: ready
Version: 2.0.0
Services: 12
Health: ready
  All systems ready
```

### health

```bash
uv run python -m jarvis health
```

Output:

```
Platform: ready
Summary: All systems ready

  ✓ security: ready - Security Platform started
  ✓ memory: ready - Memory Platform started
  ...
```

Exit code: `0` if platform is `ready` or `degraded`, `1` otherwise.

### version

```bash
uv run python -m jarvis version
# JARVIS Platform 2.0.0
```

### config

```bash
uv run python -m jarvis config
uv run python -m jarvis config --show-all
```

Shows the active configuration as JSON. The `--show-all` flag also displays the `extra` dictionary.

### logs

```bash
uv run python -m jarvis logs
uv run python -m jarvis logs --tail 100
uv run python -m jarvis logs -n 20
```

Tails the log file. Defaults to the last 50 lines.

### doctor

```bash
uv run python -m jarvis doctor
```

Runs comprehensive diagnostics and prints a report including:

- Python version and system info
- Active profile, debug mode, gateway address
- Lifecycle state and service status (with indicator symbols)
- Health check results per subsystem
- Configuration warnings (e.g., default secret key)

### test

```bash
uv run python -m jarvis test
```

Runs a platform self-test covering:

- Registry service count
- Startup order resolution
- Dependency graph integrity
- Health report validation
- Diagnostics generation

Exits with code `0` on success, `1` on any failure.

## Global Options

| Option | Description |
|---|---|
| `--config PATH` | Path to configuration root (supported by `start` and `restart`) |

## Architecture

```
CLI entry: python -m jarvis <command>
    │
    ▼
app/cli/__init__.py:main()
    │
    ├── _build_parser()      argparse with subparsers
    ├── _COMMAND_MAP         routes to app.cli.commands.<name>
    └── importlib + dispatch → cmd_<command>(args, runtime)
```

All commands receive the shared `Runtime` singleton and return an integer exit code.
