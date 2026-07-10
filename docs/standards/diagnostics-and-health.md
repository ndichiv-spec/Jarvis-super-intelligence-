# Diagnostics & Health Monitoring

## Diagnostics Framework (`app/diagnostics.py`)

The diagnostics subsystem provides a comprehensive snapshot of the running platform. It is exposed via `Runtime.diagnostics()` and the `doctor` CLI command.

### DiagnosticReport

```python
@dataclass(frozen=True)
class DiagnosticReport:
    timestamp: datetime
    platform_info: dict        # system, release, machine, hostname
    python_info: dict          # version, executable, argv
    config_summary: dict       # profile, debug, log_level, gateway_host, gateway_port, database_url, redis_url
    services: list[dict]       # id, name, version, status, health, capabilities
    lifecycle: dict            # state, history[{from, to, reason}]
    health: dict               # platform, summary, checks[{subsystem, status, message}]
    dependency_graph: dict     # service_id → [dependency_ids]
    warnings: list[str]
```

### generate_report(kernel)

Collects data from across all kernel subsystems:

```python
from app.diagnostics import generate_report, print_report

report = generate_report(kernel)
# Access specific sections:
report.platform_info      # OS / host info
report.python_info        # interpreter details
report.config_summary     # active configuration subset
report.services           # all registered services with status
report.lifecycle          # current state + transition history
report.health             # aggregated health report
report.dependency_graph   # service dependency topology
report.warnings           # configuration warnings
```

### print_report(report)

Serializes the `DiagnosticReport` to pretty-printed JSON on stdout.

### Warning Detection

The diagnostics system automatically detects and reports common misconfigurations:

| Condition | Warning |
|---|---|
| Default secret key | `"Default secret key in use — set JARVIS_APP__SECRET_KEY"` |

## Health Monitoring (`app/health.py`)

The `HealthMonitor` tracks per-subsystem health status and aggregates into a platform-level health report.

### HealthStatus Priority

Health statuses have a strict severity order:

```
error > warning > ready > unknown
```

The platform status inherits the worst status across all subsystems.

### HealthMonitor API

```python
monitor = HealthMonitor()

# Record a health check
check = monitor.report(
    subsystem="security",
    status=HealthStatus.ready,
    message="Security Platform started",
    latency_ms=12.5
)

# Retrieve a specific check
check = monitor.get("security")

# Get aggregated report
report = monitor.get_report()
```

### Health Aggregation Rules

`get_report()` applies these rules:

| Condition | Platform Status | Summary |
|---|---|---|
| No checks registered | `unknown` | `"No health checks reported"` |
| Any check is `error` | `error` | `"Errors detected"` |
| Any check is `warning` | `warning` | `"Warnings detected"` |
| Any check is `ready` | `ready` | `"All systems ready"` |
| Fallback (only `unknown` checks) | `unknown` | `"Some subsystems not yet reported"` |

### Health Check Lifecycle

The health of each subsystem evolves through the bootstrap process:

```
Registration:   unknown   ("Registered")
                        ↓
Service start:  ready    ("<Service Name> started")
                        ↓
Runtime:        ready / warning / error
```

If any service fails to start, the platform enters `degraded` state and the health report reflects the failure.

### HealthCheck Data Structure

```python
@dataclass(frozen=True)
class HealthCheck:
    subsystem: str       # service ID (e.g., "security", "ai")
    status: HealthStatus # ready | warning | error | unknown
    message: str         # human-readable description
    latency_ms: float    # optional measurement in milliseconds
    checked_at: datetime # UTC timestamp
```

### HealthReport Data Structure

```python
@dataclass(frozen=True)
class HealthReport:
    platform: HealthStatus           # aggregated status
    checks: tuple[HealthCheck, ...]  # all individual checks
    summary: str                     # human-readable summary
    timestamp: datetime              # report generation time
```

## CLI Integration

### doctor command

```
uv run python -m jarvis doctor
```

Output includes:

- Python version and system platform
- Active profile, debug mode, gateway address
- Lifecycle state
- Service list with status symbols (✓ running / ✗ failed / ? other)
- Health summary with per-subsystem breakdown
- Configuration warnings

### health command

```
uv run python -m jarvis health
```

Returns platform status, summary, and per-subsystem health checks. Exit code `0` for ready/degraded, `1` for error.
