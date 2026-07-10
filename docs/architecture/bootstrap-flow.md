# Bootstrap Flow

The bootstrap sequence transforms the platform from a cold start to a fully operational state. The entry point is `Runtime.start()` or, equivalently, `python -m jarvis start`.

## Entry Point

```
CLI (start command)
  │
  ▼
Runtime.start(config_path)
  │
  ▼
bootstrap(config_path)          [app/bootstrap.py]
  │
  ├── configure_logging()       [app/log.py]
  ├── run_startup(config_path)  [app/startup.py]
  └── install_signal_handlers() [app/shutdown.py]
```

## `run_startup()` — Detailed Sequence

The startup follows a strict 5-phase order based on the dependency graph:

```
run_startup(config_path)
  │
  ├── Phase 1: CONFIGURATION
  │     ConfigurationLoader.resolve()
  │       ├── load_defaults()         system defaults
  │       ├── load_dotenv()           .env file overrides
  │       ├── load_profile()          profiles/{profile}.json
  │       └── load_environment()      JARVIS_* env vars
  │     ConfigurationLoader.validate()
  │     configure_logging(level, log_file)  re-configure with resolved settings
  │
  ├── Phase 2: ENVIRONMENT VALIDATION
  │     EnvironmentValidator.validate_all()
  │       ├── _check_python_version()     3.13+ required
  │       ├── _check_writable_dirs()      data/, plugins/, config/
  │       ├── _check_config()             secret key, validity
  │       └── _check_optional_services()  Redis, Qdrant detection
  │     ⚠ Critical failures raise StartupError
  │
  ├── Phase 3: KERNEL INITIALIZATION
  │     AppKernel(config)
  │       ├── Lifecycle: created → initializing → starting
  │       ├── Register 12 platform services (ServiceRegistry)
  │       └── Each registered → HealthMonitor.report(unknown)
  │
  ├── Phase 4: SERVICE STARTUP (topological order)
  │     registry.resolve_startup_order()
  │       └── Topological sort of dependency graph
  │     For each service (in order):
  │       ├── registry.update_status(running)
  │       └── health.report(ready)
  │
  ├── Phase 5: READY / DEGRADED
  │     If all services running:
  │       └── Lifecycle: starting → ready
  │     If any services failed:
  │       └── Lifecycle: starting → degraded
  │
  └── print_banner(kernel, elapsed)
        └── Version, gateway URL, service count, timing
```

## Startup Order (Dependency Graph)

The topological sort resolves based on declared dependencies:

```
infrastructure          (no deps)
security                (no deps)
  ├── memory            (depends: security)
  ├── ai                (depends: security)
  ├── communication     (depends: security)
  ├── extensions        (depends: security)
  ├── knowledge         (depends: security, memory)
  │     └── agents      (depends: ai, memory, knowledge, communication)
  ├── gateway           (depends: security, infrastructure)
  │     ├── enterprise  (depends: security, gateway)
  │     └── orchestration (depends: gateway, automation)
  └── automation        (depends: security, communication)
```

Actual resolved order (as produced by `resolve_startup_order()`):

1. `infrastructure`
2. `security`
3. `memory`
4. `ai`
5. `communication`
6. `extensions`
7. `knowledge`
8. `agents`
9. `gateway`
10. `enterprise`
11. `automation`
12. `orchestration`

## Signal Handlers

After `run_startup()` completes, `install_signal_handlers()` registers handlers:

```
install_signal_handlers(kernel)
  ├── signal.signal(SIGINT,  _signal_handler)
  └── signal.signal(SIGTERM, _signal_handler)
        └── _signal_handler()
              └── run_shutdown(kernel)
                    └── sys.exit(0)
```

The shutdown runs in reverse startup order (last started, first stopped).

## Startup Timing

Elapsed time is measured from `time.perf_counter()` at the start of `run_startup()` to just before `print_banner()`. The total is displayed in the banner output.
