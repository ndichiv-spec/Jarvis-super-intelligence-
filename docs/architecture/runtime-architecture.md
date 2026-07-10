# Runtime Architecture

The JARVIS Application Runtime (EPIC-001) is the core execution environment that bootstraps, orchestrates, and manages the platform lifecycle. It follows a layered composition pattern with a single `Runtime` facade.

## Module Map

| Module | Path | Role |
|---|---|---|
| `Bootstrap` | `app/bootstrap.py` | Entry point — wires config, startup, and shutdown |
| `ConfigurationLoader` | `app/configuration.py` | Layered config from defaults, `.env`, profiles, env vars |
| `EnvironmentValidator` | `app/environment.py` | Pre-flight checks for Python, directories, config, optional services |
| `Structured Logging` | `app/log.py` | `configure_logging()` with text/JSON format, console + file |
| `AppKernel` | `app/kernel.py` | Central orchestrator — holds lifecycle, registry, health, state |
| `LifecycleManager` | `app/lifecycle.py` | Finite state machine for platform transitions |
| `ServiceRegistry` | `app/registry.py` | Service registration, discovery, dependency graph, startup ordering |
| `HealthMonitor` | `app/health.py` | Per-subsystem health checks and consolidated report |
| `Startup` | `app/startup.py` | `run_startup()` — ordered bootstrap sequence |
| `Shutdown` | `app/shutdown.py` | `run_shutdown()` — graceful reverse-order teardown + signal handlers |
| `Banner` | `app/banner.py` | Startup display with version, services, gateway info |
| `Diagnostics` | `app/diagnostics.py` | Comprehensive platform report (env, config, services, health) |
| `CLI` | `app/cli/` | Argument parser and command dispatcher |
| `Runtime` | `app/runtime.py` | Facade wrapping bootstrap, kernel, and CLI access |

## Composition Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Runtime (facade)                     │
│  start() │ stop() │ restart() │ health() │ status()     │
│  diagnostics()                                           │
└────────┬────────────┬───────────────────┬───────────────┘
         │            │                   │
         ▼            ▼                   ▼
  ┌──────────┐ ┌──────────┐ ┌────────────────────┐
  │Bootstrap │ │ AppKernel│ │ Diagnostics         │
  │  .py     │ │  .py     │ │  .py                │
  └────┬─────┘ └──┬───────┘ └────────────────────┘
       │          │
       ▼          ├──► LifecycleManager
  ┌──────────┐    ├──► ServiceRegistry
  │Startup   │    ├──► HealthMonitor
  │  .py     │    └──► KernelState
  └────┬─────┘
       │
       ├──► ConfigurationLoader
       ├──► EnvironmentValidator
       ├──► Banner
       └──► Structured Logging
```

## Module Responsibilities

### Runtime (`app/runtime.py`)
The public-facing facade. It holds a `BootstrapContext` and delegates to `AppKernel`. All CLI commands interact through this class. Key methods:

- `start(config_path)` — calls `bootstrap()`, returns the kernel
- `stop()` — calls `BootstrapContext.shutdown()`
- `restart(config_path)` — stop then start
- `health()` — returns dict with platform health status, summary, checks
- `status()` — returns dict with lifecycle state, service count, version
- `diagnostics()` — returns a `DiagnosticReport`

### AppKernel (`app/kernel.py`)
Central orchestrator that owns the four subsystems:

- `LifecycleManager` — tracks state transitions
- `ServiceRegistry` — manages 12 platform services with dependency resolution
- `HealthMonitor` — per-service health tracking
- `KernelState` — immutable dataclass with version, started_at, initialized flag

### Bootstrap (`app/bootstrap.py`)
Top-level entry point. Calls `configure_logging()`, then `run_startup()`, then `install_signal_handlers()`. Returns a `BootstrapContext` that wraps the kernel and provides `shutdown()`.

### ServiceRegistry (`app/registry.py`)
Immutable `ServiceHandle` dataclass instances are registered. Supports:

- `register()` — add a service (raises on duplicate)
- `get()` / `list()` — lookup and enumeration
- `update_status()` / `update_health()` — immutable update pattern
- `get_dependency_graph()` — returns `dict[str, list[str]]` of service → dependencies
- `resolve_startup_order()` — topological sort on the dependency graph; detects circular deps

### LifecycleManager (`app/lifecycle.py`)
Strict state machine with validated transitions. Records every transition as a `LifecycleEvent` in an append-only history list.

### HealthMonitor (`app/health.py`)
Stores `HealthCheck` per subsystem. `get_report()` aggregates the worst status across all checks using priority: error > warning > ready > unknown.

### Structured Logging (`app/log.py`)
`StructuredFormatter` supports text and JSON formats. `configure_logging()` sets up root logger with console handler and optional file handler.

### ConfigurationLoader (`app/configuration.py`)
Four-layer resolution: defaults → `.env` → profile JSON → `JARVIS_*` env vars. Tracks each value's source. Final `resolve()` creates an immutable `AppConfig`.

### EnvironmentValidator (`app/environment.py`)
Runs four checks: Python version (3.13+ required), writable directories, configuration validity, optional service detection (Redis, Qdrant).

## Data Flow

```
CLI ──► Runtime ──► Bootstrap ──► run_startup()
                                      │
                           ┌──────────┼──────────┐
                           ▼          ▼          ▼
                    Configuration   Environment  Kernel
                    Loader         Validator    Init
                           │          │          │
                           └──────────┴──────────┘
                                      │
                                      ▼
                              Service Startup
                              (topological order)
                                      │
                                      ▼
                              Banner / Ready
```

## Platform Services

The kernel registers 12 platform services with explicit dependency declarations:

| ID | Dependencies | Capabilities |
|---|---|---|
| `security` | — | authn, authz, rbac |
| `memory` | security | store, retrieve, search |
| `knowledge` | security, memory | index, search, classify |
| `ai` | security | inference, embedding |
| `communication` | security | events, commands, messaging |
| `automation` | security, communication | workflows, triggers |
| `extensions` | security | plugins, lifecycle, manifest |
| `infrastructure` | — | database, cache, storage, search |
| `gateway` | security, infrastructure | routing, middleware, protocols |
| `orchestration` | gateway, automation | coordination, scheduling |
| `agents` | ai, memory, knowledge, communication | agent, lifecycle, tasks |
| `enterprise` | security, gateway | orgs, workspaces, governance |

Topological resolution produces the startup order respecting these dependency chains.
