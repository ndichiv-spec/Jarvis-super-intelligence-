# JARVIS Mobile Architecture

## Overview

JARVIS Mobile is the official mobile companion for the JARVIS AI Ecosystem, built with Flutter and Dart. It provides secure, fast, and context-aware access to the JARVIS platform from smartphones and tablets.

## Architecture Principles

- **Clean Architecture**: Separation of concerns across domain, data, and presentation layers
- **Unidirectional Data Flow**: UI responds to state changes from providers
- **Dependency Inversion**: High-level modules do not depend on low-level modules
- **Gateway-Only Communication**: All business logic resides server-side; the mobile app communicates exclusively through the Professional Service Gateway

## Layer Structure

### Domain Layer
Core business entities and repository interfaces. Contains no framework dependencies.

```
lib/domain/
  entities/          # Core business objects (Conversation, Message, Project, etc.)
  repositories/      # Abstract repository interfaces
  usecases/          # Application-specific business rules
```

### Data Layer
Implements domain interfaces and handles data sourcing/ persistence.

```
lib/data/
  datasources/       # Remote API data sources
  models/            # JSON-serializable data models
  repositories/      # Repository implementations
```

### Presentation Layer
Flutter UI and Riverpod state management.

```
lib/presentation/
  pages/             # Screen layouts
  providers/         # Riverpod state notifiers
  widgets/           # Reusable UI components
```

## State Management

Riverpod is used for state management with `StateNotifierProvider` for complex state and `Provider` for dependency injection.

- `AuthNotifier` - authentication state
- `ConversationNotifier` - conversations and messages
- `ProjectNotifier` - project management
- `MemoryNotifier` - memory browsing
- `KnowledgeNotifier` - knowledge search
- `AutomationNotifier` - workflow management
- `NotificationNotifier` - notification handling
- `QuickActionNotifier` - quick actions
- `SecurityNotifier` - session/device management
- `SettingsNotifier` - app preferences
- `DiagnosticsNotifier` - app health monitoring

## Navigation

- Bottom navigation bar with 4 primary tabs: Home, Workspace, Activity, Account
- Push navigation for sub-pages (AI Workspace, Memory Center, etc.)
- Auth-gated: `main.dart` shows LoginPage or HomePage based on authentication state

## Theme

Full Material 3 support with:
- Light and dark themes
- Custom color scheme (primary, secondary, accent, semantic colors)
- Typography scale using Inter font
- Responsive spacing constants
