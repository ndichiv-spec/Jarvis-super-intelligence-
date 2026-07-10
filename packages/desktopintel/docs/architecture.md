# Desktop Architecture

## System Overview

JARVIS Desktop Intelligence is a cross-platform desktop application built on **Tauri v2** with a **Rust** backend and a **Next.js + React** frontend. It provides a secure, sandboxed environment for AI-augmented desktop workflows including file interaction, synchronization, offline mode, notifications, and integration with the JARVIS Service Gateway.

```
┌────────────────────────────────────────────────────────────┐
│                    Desktop Shell (Tauri v2)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Next.js + React UI (WebView)            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │  │
│  │  │Dashboard │ │  Sync    │ │Settings  │ │Updates │ │  │
│  │  ├──────────┤ ├──────────┤ ├──────────┤ ├────────┤ │  │
│  │  │Perms Ctr│ │ Notifs   │ │Integrate │ │Offline │ │  │
│  │  ├──────────┤ ├──────────┤ ├──────────┤ ├────────┤ │  │
│  │  │File Int.│ │Diagnose  │ │  Audit   │ │Cmd Pal │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │  │
│  │           ┌─────────────────────────────┐            │  │
│  │           │   Zustand State (desktop-   │            │  │
│  │           │   store.ts / ui-store.ts)   │            │  │
│  │           └──────────┬──────────────────┘            │  │
│  │                      │ invoke()                      │  │
│  └──────────────────────┼───────────────────────────────┘  │
│                         │ Tauri IPC                       │
│  ┌──────────────────────┼───────────────────────────────┐  │
│  │        Rust Backend  │  (Tauri Commands)             │  │
│  │  ┌───────────────────┴───────────────────────────┐   │  │
│  │  │               lib.rs (Builder)                │   │  │
│  │  │  Plugin Init  │  State Management  │  Handler │   │  │
│  │  └───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──┘   │  │
│  │  ┌────┘   │   │   │   │   │   │   │   │   │   └────┐ │  │
│  │  ▼        ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼   ▼       ▼ │  │
│  │ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ │  │
│  │ │RT│ │PM│ │SM│ │FI│ │IR│ │NC│ │OM│ │UM│ │CR│ │SM│ │  │
│  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │
│  │ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ │  │
│  │                          ┌────────┐ ┌────────┐      │  │
│  │                          │Diag    │ │Audit   │      │  │
│  │                          │Coll    │ │Logger  │      │  │
│  │                          └────────┘ └────────┘      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Tauri Plugins (OS Bridge)                  │  │
│  │  Shell │ Dialog │ Notification │ Clipboard │ FS     │  │
│  │  Process │ Updater                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐
│ JARVIS Service     │
│ Gateway            │
│ (AI / Sync Cloud)  │
└────────────────────┘
```

## Module Architecture

| Module | Rust Module | Description |
|--------|-------------|-------------|
| **Runtime** | `runtime/` | Session lifecycle, capability discovery, gateway connectivity, uptime tracking |
| **Permissions** | `permissions/` | Permission request/grant/deny/revoke lifecycle, audit integration, privacy enforcement |
| **Sync** | `sync/` | Workspace synchronization for conversations, knowledge, settings; conflict resolution |
| **File Interaction** | `file_interaction/` | Native file dialog (open/save), file operation recording |
| **Integrations** | `integrations/` | Integration contract registry (Git, GitHub, Slack, VS Code, Docker, Browser, etc.) |
| **Notifications** | `notifications/` | In-app notification center, native OS notification delivery |
| **Offline** | `offline/` | Offline mode toggle, conversation/knowledge caching, action queue, sync-on-reconnect |
| **Updates** | `updates/` | Update checking, release channels (stable/beta/nightly), download progress |
| **Command Palette** | `palette/` | Keyboard-driven command registry with search and category filtering |
| **Settings** | `settings/` | Persisted settings (window, theme, sync, notifications, privacy, offline, updates) |
| **Diagnostics** | `diagnostics/` | Health checks for runtime, gateway, sync, and resource usage |
| **Audit** | `audit/` | Immutable event log for security-relevant actions across all modules |

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Desktop Shell | Tauri | 2.x |
| Backend Language | Rust | 2021 edition |
| Async Runtime | Tokio | 1.x (full features) |
| Web Framework (Backend) | Tauri | 2.x |
| Frontend Framework | Next.js | 14.2 |
| UI Library | React | 18.3 |
| State Management | Zustand | 4.5 |
| Styling | Tailwind CSS | 3.4 |
| UI Components | Radix UI | Primitive set |
| Charts | Recharts | 2.12 |
| Animations | Framer Motion | 11.2 |
| HTTP Client | reqwest | 0.12 |
| Serialization | serde / serde_json | 1.x |
| UUID | uuid | 1.x (v4) |
| Date/Time | chrono | 0.4 |
| Logging | tracing + tracing-subscriber | 0.1 / 0.3 |
| Testing (Rust) | built-in `#[test]` | — |
| Testing (Frontend) | Vitest + Testing Library | 1.6 / 15.0 |
| Packaging | Tauri Bundler (`.msi`, `.dmg`, `.AppImage`) | 2.x |

## Data Flow

Communication between the React frontend and the Rust backend uses **Tauri's IPC mechanism** via `invoke()`:

```
React Component
    │
    ▼
commands.ts  ───►  invoke("command_name", args)
    │
    ├── Tauri available?  ──►  @tauri-apps/api/core.invoke()
    │                              │
    │                              ▼
    │                         Rust #[tauri::command]
    │                              │
    │                         ┌────┴────┐
    │                         │  Access  │
    │                         │ Managed  │
    │                         │  State   │
    │                         └────┬────┘
    │                              │
    │                         ┌────┴────┐
    │                         │ Execute  │
    │                         │ Business │
    │                         │  Logic   │
    │                         └────┬────┘
    │                              │
    │                         Return serde
    │                         Serializeable
    │                              │
    └── Tauri unavailable?  ──►  mockInvoke()
                                      │
                                  Return mock
                                  data for dev

State Update:
    invoke response  ──►  desktop-store.ts (Zustand set())
                              │
                         React re-render via
                         useDesktopStore hook
```

### Command Categories

- **Queries**: `get_runtime_status`, `get_permissions`, `get_sync_status`, `get_offline_status`, `get_update_status`, `get_diagnostics`, `get_commands`, `get_settings`, `get_notifications`, `get_file_operations`, `get_integration_contracts`, `get_audit_events`, `get_cached_conversations`, `get_cached_knowledge`, `get_queued_actions`
- **Mutations**: `request_permission`, `grant_permission`, `deny_permission`, `revoke_permission`, `trigger_sync`, `toggle_offline`, `check_updates`, `apply_settings`, `mark_notification_read`, `clear_notifications`, `open_file`, `save_file`

## Security Architecture

### Permission Model

All privileged operations go through the `PermissionCenter`:

```
Request ──► Pending ──► Grant/Deny ──► Revoke/Expire
              │
         User reviews
         in Permission Center UI
```

Each permission request is logged in the `AuditLogger` with timestamp, module, action, and outcome.

### Audit Trail

The `AuditLogger` module records every security-relevant event:

- Permission requests, grants, denials, revocations
- File open/save operations
- Sync initiation and completion
- Clipboard read/write attempts
- Notification sends

Events are filterable by module and action, visible in the Audit Log page.

### Privacy Enforcement

- No automatic file system scanning
- No background surveillance or continuous monitoring
- All file access requires explicit user permission per session
- Clipboard access is always user-initiated and permission-gated
- Telemetry is opt-in (defaults to off)
- Local processing mode available to keep data on-device

## Communication

| Path | Mechanism | Purpose |
|------|-----------|---------|
| React ↔ Rust | Tauri `invoke()` | Command execution with typed args/responses |
| React ↔ Rust | Tauri events | Real-time notifications (future) |
| Rust → Gateway | `reqwest` HTTP | Sync, integration calls, AI inference |
| Rust ← Gateway | Polling / SSE | Update checks, remote notifications |

## Clean Architecture Layers

```
┌────────────────────────────────────────┐
│           Presentation Layer           │
│   Next.js Pages / React Components     │
│   Zustand Stores                       │
├────────────────────────────────────────┤
│          Interface Adapters            │
│   commands.ts (invoke wrappers)        │
│   Tauri #[tauri::command] handlers     │
├────────────────────────────────────────┤
│           Application Layer            │
│   State managers (PermissionCenter,    │
│   SyncManager, OfflineManager, etc.)   │
├────────────────────────────────────────┤
│            Domain Layer                │
│   Core types, enums, business logic    │
│   (PermissionType, SyncState, etc.)    │
├────────────────────────────────────────┤
│        Infrastructure Layer            │
│   Tauri plugins (FS, Dialog, etc.)     │
│   OS APIs (clipboard, notifications)   │
│   File system (settings.json)          │
│   Network (reqwest → Gateway)          │
└────────────────────────────────────────┘
```
