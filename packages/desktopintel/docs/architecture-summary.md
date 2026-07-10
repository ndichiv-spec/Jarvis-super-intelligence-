# JARVIS Desktop Intelligence — Architecture Summary

## Overview

JARVIS Desktop Intelligence is the secure cross-platform desktop runtime companion for the JARVIS AI Ecosystem. It provides user-authorized interaction with desktop operating systems — executing approved tasks, integrating with local applications, and delivering a seamless desktop experience while preserving user privacy and platform security.

## Architecture Style

**Hybrid Desktop Application** — Tauri 2 shell wrapping a Next.js 14 webview, with Rust backend modules communicating to React/TypeScript frontend via Tauri IPC.

```
┌─────────────────────────────────────────────────┐
│                 Desktop Runtime                    │
│                                                   │
│  ┌─────────────┐     ┌───────────────────────┐   │
│  │   Tauri     │────▶│   Rust Backend         │   │
│  │   WebView   │     │   (12 Modules)         │   │
│  │   (Next.js) │◀────│   · Runtime            │   │
│  │             │ IPC │   · Permissions        │   │
│  │             │     │   · Sync               │   │
│  │             │     │   · File Interaction   │   │
│  │             │     │   · Integrations       │   │
│  │             │     │   · Notifications      │   │
│  │             │     │   · Offline            │   │
│  │             │     │   · Updates            │   │
│  │             │     │   · Command Palette    │   │
│  │             │     │   · Settings           │   │
│  │             │     │   · Diagnostics        │   │
│  │             │     │   · Audit              │   │
│  └─────────────┘     └───────────┬───────────┘   │
│                                  │                │
│                                  ▼                │
│                     Service Gateway               │
│                   (HTTP / WS / SSE)               │
└─────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Desktop Shell | Tauri 2 + Rust 2021 | Native OS integration, IPC bridge, system access |
| Frontend | Next.js 14 + React 18 + TypeScript 5.4 | UI rendering in webview |
| Styling | Tailwind CSS 3.4 + Radix UI | UI components and design system |
| State | Zustand 4.5 | Client-side state management |
| IPC Bridge | Tauri Command API | Secure typed invoke/call between JS and Rust |
| Diagnostics | Recharts 2.12 | Resource usage visualization |
| Animations | Framer Motion 11.2 | UI transitions and effects |
| Icons | Lucide React 0.400 | Icon system |
| Plugins | tauri-plugin-dialog, notification, fs, clipboard, shell, updater, process | Native OS capabilities |

## Module Architecture

### Rust Backend (12 modules, 27 Tauri commands)

Each module follows Clean Architecture:
- **Types/Structs** — Domain models with serde serialization
- **Logic** — Pure functions and business rules
- **Tauri Commands** — `#[tauri::command]` wrappers for IPC

| Module | Key Types | Commands |
|--------|-----------|----------|
| Runtime | RuntimeState, RuntimeStatus | get_runtime_status |
| Permissions | PermissionType (12 variants), PermissionGrant, PermissionRequest, PermissionEvent | get_permissions, request/grant/deny/revoke_permission |
| Sync | SyncState, SyncModule, SyncStatus | get_sync_status, trigger_sync |
| FileInteraction | FileOpType, FileOperation | get_file_operations, open_file, save_file |
| Integrations | IntegrationType (6), IntegrationContract | get_integration_contracts |
| Notifications | NotificationItem | get_notifications, mark_notification_read, clear_notifications |
| Offline | OfflineStatus, CachedConversation, CachedKnowledge, QueuedAction | get_offline_status, toggle_offline, get_cached_* |
| Updates | ReleaseChannel (3), UpdateStatus | get_update_status, check_updates |
| Palette | CommandCategory (6), DesktopCommand | get_commands |
| Settings | DesktopSettings (6 subgroups) | get_settings, apply_settings |
| Diagnostics | RuntimeHealth, GatewayHealth, SyncHealth, ResourceUsage | get_diagnostics |
| Audit | AuditEvent | get_audit_events |

### React/Next.js Frontend (11 pages, 14 UI components, 5 shared components)

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `dashboard` | Runtime status, metrics, quick actions |
| Permission Center | `permissions` | 3 tabs: Granted/Pending/History |
| Workspace Sync | `sync` | Sync modules, status, manual sync |
| File Operations | `file-interaction` | File operation history |
| Integrations | `integrations` | Integration contracts registry |
| Notifications | `notifications` | Notification history |
| Offline Mode | `offline-mode` | Cache management, queued actions |
| Updates | `updates` | Version info, channel management |
| Diagnostics | `diagnostics` | Health, connectivity, resources |
| Audit Log | `audit` | Audit trail viewer |
| Settings | `settings` | Full settings management |

## Data Flow

```
User Action → React Component → Zustand Store → commands.invoke()
    → Tauri IPC → Rust Command Handler → Module Logic
    → Response → IPC Return → Store Update → Re-render
```

## Security Architecture

| Layer | Mechanism |
|-------|-----------|
| Permission Enforcement | Permission Center gates every privileged operation |
| Request Flow | Explicit request → User approval → Grant/Deny → Execute |
| Revocation | Permissions revocable at any time |
| Audit Trail | Every permission action logged with module/permission/resource/result |
| Network Isolation | All platform communication through Service Gateway only |
| No Background Ops | No background threads for monitoring, scanning, or indexing |
| UI Protection | CSP headers restrict script/content sources in webview |

## Privacy Guarantees

| Guarantee | Implementation |
|-----------|---------------|
| No automatic file scanning | `file:read` requires explicit user-selected file path |
| No clipboard monitoring | `clipboard:read` is per-use with visible request dialog |
| No screen capture | `screen:capture` requires explicit user grant |
| No audio recording | `microphone:access` requires explicit user grant |
| No hidden processes | All runtime operations visible in Diagnostics |
| Explainable actions | Permission requests show reason and source |

## Communication

- **Internal**: Tauri IPC (invoke/events) between Rust and JS
- **Platform**: Service Gateway via HTTP, WebSocket, SSE
- **Native**: OS APIs via Tauri plugins (dialog, notification, fs, clipboard, updater)

---

**Product:** JARVIS Desktop Intelligence v1.0.0
**Status:** ✅ Frozen — Ready for Integration
**Part of:** JARVIS AI Ecosystem (Phase 17)

---

*End of JARVIS Desktop Intelligence Architecture Summary*
