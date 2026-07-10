# Desktop Runtime Guide

## What the Desktop Runtime Does

The `RuntimeState` (`src-tauri/src/runtime/mod.rs`) manages the lifecycle of the desktop application. It provides:

- **Session identity** — a unique UUID per launch
- **Uptime tracking** — elapsed time since application start
- **Capability discovery** — which modules are available in this build
- **Gateway connectivity** — connection status to the JARVIS Service Gateway

## Startup Sequence

```
1. Application Launch (main.rs)
   │
   ├── 2. lib.rs :: run()
   │      │
   │      ├── 3. Tauri Builder initialized
   │      │      ├── Plugins loaded (shell, dialog, notification,
   │      │      │   clipboard-manager, fs, process, updater)
   │      │      ├── Managed state created:
   │      │      │   ├── RuntimeState (session_id = UUID v4)
   │      │      │   ├── PermissionCenter
   │      │      │   ├── SyncManager
   │      │      │   ├── FileInteraction
   │      │      │   ├── IntegrationRegistry
   │      │      │   ├── NotificationCenter
   │      │      │   ├── OfflineManager
   │      │      │   ├── UpdateManager
   │      │      │   ├── CommandRegistry
   │      │      │   ├── SettingsManager (loads from disk)
   │      │      │   ├── DiagnosticsCollector
   │      │      │   └── AuditLogger
   │      │      └── Command handlers registered
   │      │
   │      └── 4. RuntimeState::start()
   │             └── discover_capabilities()
   │                    └── Returns: [file_interaction, notifications,
   │                         sync, offline, updates, command_palette,
   │                         diagnostics, audit, permissions]
   │
   └── 5. WebView loads Next.js app
          │
          └── 6. desktop-store.ts :: initialize()
                   └── Fires 15 parallel invoke() calls to
                        populate all state from Rust backend
```

### Session Management

Each time the application starts, a new session is created:

```rust
pub struct RuntimeState {
    pub version: String,          // CARGO_PKG_VERSION
    pub started_at: DateTime<Utc>,// session start timestamp
    pub session_id: Uuid,         // unique per launch
    pub capabilities: Mutex<Vec<String>>,
    pub gateway_connected: Mutex<bool>,
}
```

The session ID is used in diagnostics and audit logging to correlate events across a single application run.

### Capability Discovery

`discover_capabilities()` returns the static list of modules compiled into the binary. This allows the frontend to detect which features are available:

- `file_interaction`
- `notifications`
- `sync`
- `offline`
- `updates`
- `command_palette`
- `diagnostics`
- `audit`
- `permissions`

The frontend can query capabilities via `get_runtime_status`.

## Shutdown Sequence

```
User closes window / Ctrl+C / OS terminate
    │
    ├── 1. RuntimeState::shutdown()
    │       └── gateway_connected = false
    │
    ├── 2. SettingsManager auto-persists (via Tauri window close event)
    │
    └── 3. Tauri tears down:
            ├── Plugin cleanup
            ├── WebView destroy
            └── Process exit
```

## Gateway Connectivity

The runtime tracks whether a connection to the JARVIS Service Gateway is established. The `gateway_connected` flag is:

- Set to `false` at initialization
- Used by diagnostics to report `GatewayHealth`
- Checked before sync operations
- Exposed via `get_runtime_status`

Gateway connection is managed externally (via the Gateway module itself); the runtime only reflects the current state.

## Runtime Health Monitoring

The `DiagnosticsCollector` collects health data across subsystems:

| Check | Source | Status Values |
|-------|--------|---------------|
| Runtime Health | `RuntimeState` | Healthy / Degraded / Unhealthy |
| Gateway Health | `RuntimeState.gateway_connected` | Healthy (connected) / Degraded (disconnected) |
| Sync Health | `SyncManager` | Healthy / Degraded (errors or pending) |
| Resource Usage | OS calls (WMI, sysinfo) | CPU %, memory MB, disk GB |

## Troubleshooting Common Issues

| Issue | Likely Cause | Check |
|-------|-------------|-------|
| Runtime status shows empty version | Build env issue | Ensure `CARGO_PKG_VERSION` is set in `Cargo.toml` |
| Session ID all zeros | UUID generation failure | Check `uuid` crate features (`v4`) |
| Capabilities list empty | `RuntimeState::start()` not called | Verify startup sequence in `lib.rs` |
| Gateway shows disconnected | Gateway not running or unreachable | Check gateway URL config; run diagnostics |
| Uptime resets unexpectedly | Process restarted | Check OS logs for crash/restart |
| Diagnostics returns 0 for resource usage | Platform not supported | Currently returns placeholder values |
