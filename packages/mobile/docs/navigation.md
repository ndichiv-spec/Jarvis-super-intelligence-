# Navigation Guide

## App Entry

```
main.dart
  ├── ProviderScope (Riverpod root)
  └── JarvisMobileApp
      ├── NOT authenticated → LoginPage
      └── Authenticated → HomePage
```

## Primary Navigation (Bottom Bar)

| Tab | Page | Description |
|-----|------|-------------|
| Home | `_HomeTab` | Dashboard with metrics, quick actions, recent conversations, active projects, running automations |
| Workspace | `ProjectWorkspacePage` | Project list with filtering |
| Activity | `NotificationPage` | Notification feed |
| Account | `_AccountTab` | Profile, links to all sub-pages |

## Sub-pages

Accessible from the Account tab:

| Page | Route | Description |
|------|-------|-------------|
| AI Workspace | `AiWorkspacePage` | Conversational AI interface |
| Memory Center | `MemoryPage` | Browse, search, archive memories |
| Knowledge Explorer | `KnowledgePage` | Browse collections, search documents |
| Automation Center | `AutomationPage` | Running/scheduled workflows |
| Security Center | `SecurityPage` | Sessions, devices, biometric unlock |
| Settings | `SettingsPage` | Appearance, notifications, offline mode |
| Diagnostics | `DiagnosticsPage` | Connectivity, sync, health status |

## Navigation Flows

### Authentication Flow
1. App launches → checks for stored session token
2. Token exists → restore session → HomePage
3. No token → LoginPage
4. Login successful → store session → HomePage

### Conversation Flow
1. Navigate to AI Workspace
2. Select/create conversation
3. Send message → stream response
4. View conversation history

### Project Flow
1. Navigate to Workspace tab
2. Select project → view details
3. Access related conversations/workflows/knowledge

## Accessibility

- All interactive elements have semantic labels
- Bottom navigation uses `NavigationBar` with Material 3
- Images have `Semantics` wrappers with descriptive labels
- Loading states are announced via `Semantics`
