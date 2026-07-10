# Mobile Platform Architecture Summary

## Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Flutter 3.4+ |
| Language | Dart 3.4+ |
| State Management | Riverpod 2.5 |
| Architecture | Clean Architecture (Domain/Data/Presentation) |
| REST Client | http package |
| Streaming | SSE (Server-Sent Events) |
| Realtime | WebSocket (web_socket_channel) |
| Local DB | SQLite (sqflite) |
| Secure Storage | FlutterSecureStorage |
| Biometrics | local_auth |
| Connectivity | connectivity_plus |
| DI | Provider pattern (Riverpod) |

## Communication Flow

```
Mobile App → Service Gateway → Backend Subsystems
     ↑              |
     └──────────────┘
  (Gateway returns standard envelope)
```

All communication goes through the Professional Service Gateway at `/gateway/*`. The mobile app never connects directly to backend services.

## Module Map

```
JARVIS Mobile
├── Mobile Runtime (main.dart)
│   ├── Session restoration
│   ├── Biometric check
│   ├── Theme initialization
│   └── Connectivity monitoring
├── Home Dashboard
│   ├── Quick actions
│   ├── Metrics grid
│   ├── Recent conversations
│   ├── Active projects
│   └── Running automations
├── AI Workspace
│   ├── Conversation selector
│   ├── Message stream (SSE)
│   └── Input/composer
├── Project Workspace
│   ├── Project list + filter
│   ├── Project details
│   └── Related entities
├── Memory Center
│   ├── Memory list
│   ├── Search
│   └── Archive/delete
├── Knowledge Explorer
│   ├── Collections
│   └── Document search
├── Automation Center
│   ├── Running workflows
│   ├── Scheduled workflows
│   └── Execution history
├── Notification Center
│   ├── Grouped feed
│   └── Read/unread management
├── Security Center
│   ├── Session management
│   └── Device management
├── Settings
│   ├── Appearance
│   ├── Security
│   └── Preferences
├── Diagnostics
│   ├── Health check
│   ├── Sync status
│   └── Offline queue
└── Offline Mode
    ├── SQLite cache
    ├── Action queue
    └── Auto-sync
```

## File Count

| Layer | Directory | Files |
|-------|-----------|-------|
| Core | lib/core/ | 19 |
| Domain | lib/domain/ | 43 |
| Data | lib/data/ | 36 |
| Presentation | lib/presentation/ | 38 |
| Tests | test/ | 6 |
| Docs | docs/ | 10 |
| **Total** | | **152** |

## Key Design Decisions

1. **Gateway exclusivity**: The mobile app communicates ONLY through the Service Gateway. No backend services are called directly. This enforces the security, rate-limiting, and observability provided by the gateway.

2. **Clean Architecture**: Domain entities have zero framework dependencies. Repository interfaces are defined in the domain layer. Data sources and UI are swappable implementations.

3. **Riverpod over BLoC**: Riverpod provides compile-time safety, better testability, and simpler DI than BLoC for this application scale.

4. **SSE over WebSocket for conversations**: SSE is simpler for server-to-client streaming (the primary pattern for AI responses). WebSocket is available for bidirectional needs.

5. **SQLite offline queue**: Actions are serialized to SQLite and replayed when connectivity returns, ensuring no user actions are lost during offline periods.

6. **Platform biometrics**: Using platform-native biometric APIs through `local_auth` for secure, standards-compliant authentication.
