# Runtime API Reference

## Runtime (`app/runtime.py`)

Public facade for the entire platform. CLI commands interact exclusively through this class.

```python
class Runtime:
    def __init__(self) -> None: ...

    # ── Properties ──
    @property
    def kernel(self) -> AppKernel | None: ...
    @property
    def config(self) -> AppConfig | None: ...
    @property
    def registry(self) -> ServiceRegistry | None: ...
    @property
    def state(self) -> KernelState | None: ...

    # ── Lifecycle ──
    def start(self, config_path: str = "") -> AppKernel: ...
    def stop(self) -> None: ...
    def restart(self, config_path: str = "") -> AppKernel: ...

    # ── Observability ──
    def health(self) -> dict: ...
    def status(self) -> dict: ...
    def diagnostics(self) -> DiagnosticReport: ...
```

**`start(config_path: str = "") -> AppKernel`**
Bootstraps the platform. Calls `bootstrap(config_path)` which runs `run_startup()`, registers signal handlers, and returns the initialized kernel.

**`stop() -> None`**
Calls `BootstrapContext.shutdown()` which runs `run_shutdown(kernel)`.

**`restart(config_path: str = "") -> AppKernel`**
Stop then start. Returns the new kernel.

**`health() -> dict`**
Returns a dictionary with platform health status. Keys: `platform` (str), `summary` (str), `checks` (list of `{subsystem, status, message}`).

**`status() -> dict`**
Returns `{status, services, version}`. `status` is the lifecycle state string.

**`diagnostics() -> DiagnosticReport`**
Returns the full `DiagnosticReport`. Raises `RuntimeError` if kernel is not running.

---

## AppKernel (`app/kernel.py`)

Central orchestrator owned by `Runtime`.

```python
class AppKernel:
    def __init__(self, config: AppConfig | None = None) -> None: ...

    @property
    def config(self) -> AppConfig: ...
    @property
    def lifecycle(self) -> LifecycleManager: ...
    @property
    def registry(self) -> ServiceRegistry: ...
    @property
    def health(self) -> HealthMonitor: ...
    @property
    def state(self) -> KernelState: ...

    def initialize(self) -> None: ...
    def mark_ready(self) -> None: ...
    def mark_degraded(self, reason: str = "") -> None: ...
    def shutdown(self) -> None: ...
    def fail(self, reason: str = "") -> None: ...
    def get_health_report(self) -> HealthReport: ...
```

**`initialize()`** — transitions through `created → initializing → starting`, registers all 12 platform services with `HealthStatus.unknown`.

**`mark_ready()`** — sets `KernelState.initialized = True`, records `started_at`, transitions to `ready`.

**`mark_degraded(reason)`** — transitions to `degraded`. Can recover back to `ready`.

**`shutdown()`** — transitions `stopping → stopped`.

**`fail(reason)`** — transitions to `failed` (terminal).

### KernelState

```python
@dataclass(frozen=True)
class KernelState:
    initialized: bool = False
    services_count: int = 0
    started_at: datetime | None = None
    version: str = "2.0.0"
```

---

## LifecycleManager (`app/lifecycle.py`)

Finite state machine for platform lifecycle.

```python
class LifecycleManager:
    def __init__(self) -> None: ...

    @property
    def state(self) -> LifecycleState: ...
    @property
    def history(self) -> list[LifecycleEvent]: ...

    def transition(self, target: LifecycleState, reason: str = "") -> LifecycleState: ...
    def can_transition_to(self, target: LifecycleState) -> bool: ...
    def elapsed_in_state(self) -> float: ...
```

**`transition(target, reason)`** — validates the transition against `_VALID_TRANSITIONS`, records a `LifecycleEvent`, updates state. Raises `LifecycleError` on invalid transition.

**`can_transition_to(target)`** — returns `True` if the transition is valid from the current state.

**`elapsed_in_state()`** — seconds since the last transition. Returns `0.0` if no transitions have occurred.

### LifecycleState

```python
class LifecycleState(StrEnum):
    created = "created"
    initializing = "initializing"
    starting = "starting"
    ready = "ready"
    degraded = "degraded"
    stopping = "stopping"
    stopped = "stopped"
    failed = "failed"
```

### LifecycleEvent

```python
@dataclass(frozen=True)
class LifecycleEvent:
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime
    reason: str
```

---

## ServiceRegistry (`app/registry.py`)

Manages service registration, discovery, and dependency ordering.

```python
class ServiceRegistry:
    def __init__(self) -> None: ...

    def register(self, handle: ServiceHandle) -> ServiceHandle: ...
    def get(self, service_id: str) -> ServiceHandle | None: ...
    def list(self) -> list[ServiceHandle]: ...
    def update_status(self, service_id: str, status: ServiceStatus) -> ServiceHandle | None: ...
    def update_health(self, service_id: str, health: HealthStatus) -> ServiceHandle | None: ...
    def count(self) -> int: ...
    def get_dependency_graph(self) -> dict[str, list[str]]: ...
    def resolve_startup_order(self) -> list[str]: ...
```

**`register(handle)`** — adds a service. Raises `ValueError` if the ID already exists.

**`update_status(id, status)`** — immutable update pattern: creates a new `ServiceHandle` with the new status. Raises `ValueError` if service not found.

**`update_health(id, health)`** — same immutable update for health status. Returns `None` if service not found.

**`get_dependency_graph()`** — returns `{service_id: [dependency_ids]}`.

**`resolve_startup_order()`** — topological sort of the dependency graph. Raises `ValueError` on circular dependency.

### ServiceHandle

```python
@dataclass(frozen=True)
class ServiceHandle:
    id: str = ""
    name: str = ""
    version: str = "0.1.0"
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    status: ServiceStatus = ServiceStatus.registered
    health: HealthStatus = HealthStatus.unknown
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = ...
```

### ServiceStatus

```python
class ServiceStatus(StrEnum):
    registered = "registered"
    initializing = "initializing"
    running = "running"
    degraded = "degraded"
    stopped = "stopped"
    failed = "failed"
```

---

## HealthMonitor (`app/health.py`)

Per-subsystem health tracking and aggregation.

```python
class HealthMonitor:
    def __init__(self) -> None: ...

    def report(self, subsystem: str, status: HealthStatus, message: str = "", latency_ms: float = 0.0) -> HealthCheck: ...
    def get(self, subsystem: str) -> HealthCheck | None: ...
    def get_report(self) -> HealthReport: ...
```

**`report(subsystem, status, message, latency_ms)`** — records or updates a health check for the given subsystem.

**`get(subsystem)`** — returns the current `HealthCheck` or `None`.

**`get_report()`** — aggregates all checks into a `HealthReport`. Platform status priority: `error > warning > ready > unknown`.

### HealthStatus

```python
class HealthStatus(StrEnum):
    ready = "ready"
    warning = "warning"
    error = "error"
    unknown = "unknown"
```

### HealthCheck

```python
@dataclass(frozen=True)
class HealthCheck:
    subsystem: str = ""
    status: HealthStatus = HealthStatus.unknown
    message: str = ""
    latency_ms: float = 0.0
    checked_at: datetime = ...
```

### HealthReport

```python
@dataclass(frozen=True)
class HealthReport:
    platform: HealthStatus = HealthStatus.unknown
    checks: tuple[HealthCheck, ...] = ()
    summary: str = ""
    timestamp: datetime = ...
```

---

## ConfigurationLoader (`app/configuration.py`)

Layered configuration loader with source tracking.

```python
class ConfigurationLoader:
    def __init__(self, root: str | Path | None = None) -> None: ...

    def load_defaults(self) -> None: ...
    def load_dotenv(self, path: str | Path | None = None) -> None: ...
    def load_profile(self, name: str | None = None) -> None: ...
    def load_environment(self) -> None: ...
    def resolve(self) -> AppConfig: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def validate(self) -> list[str]: ...
```

**`resolve()`** — calls all four load methods in order (defaults → dotenv → profile → environment) and returns an `AppConfig` instance.

**`validate()`** — checks required keys exist. Returns a list of issue strings.

### AppConfig

```python
@dataclass(frozen=True)
class AppConfig:
    debug: bool = False
    log_level: str = "info"
    log_file: str = ""
    profile: str = "development"
    home_url: str = "http://localhost:3000"
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    data_dir: str = "data"
    plugins_dir: str = "plugins"
    config_dir: str = "config"
    database_url: str = "sqlite:///data/jarvis.db"
    redis_url: str = ""
    qdrant_url: str = "http://localhost:6333"
    secret_key: str = "change-me-in-production"
    extra: dict[str, Any] = field(default_factory=dict)
```

---

## EnvironmentValidator (`app/environment.py`)

Pre-flight validation checks.

```python
class EnvironmentValidator:
    def __init__(self, config: AppConfig | None = None) -> None: ...
    def validate_all(self) -> list[EnvCheck]: ...
```

**`validate_all()`** — runs four checks and returns a list of `EnvCheck`:

| Check | Description | Severity |
|---|---|---|
| `_check_python_version()` | Requires Python ≥ 3.13 | `critical` |
| `_check_writable_dirs()` | Verifies data/, plugins/, config/ directories are writable | `warning` |
| `_check_config()` | Validates config is loaded and secret key is not default | `warning` |
| `_check_optional_services()` | Reports configured Redis/Qdrant URLs | `warning` |

### EnvCheck

```python
@dataclass(frozen=True)
class EnvCheck:
    name: str = ""
    status: str = "ok"        # "ok" | "error" | "warning"
    message: str = ""
    severity: str = "warning"  # "warning" | "critical"
```

---

## Diagnostics (`app/diagnostics.py`)

Platform introspection and reporting.

```python
def generate_report(kernel: AppKernel) -> DiagnosticReport: ...
def print_report(report: DiagnosticReport) -> None: ...
```

**`generate_report(kernel)`** — gathers system info, Python info, config summary, services, lifecycle history, health report, dependency graph, and warnings.

### DiagnosticReport

```python
@dataclass(frozen=True)
class DiagnosticReport:
    timestamp: datetime
    platform_info: dict        # system, release, machine, hostname
    python_info: dict          # version, executable, argv
    config_summary: dict       # profile, debug, log_level, gateway, db, redis
    services: list[dict]       # id, name, version, status, health, capabilities
    lifecycle: dict            # state, history
    health: dict               # platform, summary, checks
    dependency_graph: dict     # service_id → [dependency_ids]
    warnings: list[str]
```
