# Developer Guide

## Prerequisites

- Flutter SDK ^3.4.0
- Dart ^3.4.0
- Android Studio / Xcode for device builds

## Setup

```bash
cd packages/mobile
flutter pub get
```

## Project Structure

```
lib/
  main.dart                      # App entry point
  core/                          # Cross-cutting concerns
    constants/                   # API paths, app constants
    errors/                      # Exception hierarchy
    extensions/                  # Context and date extensions
    network/                     # HTTP client, SSE, WebSocket, connectivity, DB, offline queue
    security/                    # Biometric auth, secure storage
    theme/                       # Colors, typography, spacing
    utils/                       # Result type, formatters
  data/                          # Data layer
    datasources/                 # Remote API data sources
    models/                      # JSON data models
    repositories/                # Repository implementations
  domain/                        # Domain layer
    entities/                    # Business entities
    repositories/                # Abstract repository interfaces
    usecases/                    # Business use cases
  presentation/                  # Presentation layer
    pages/                       # Screen widgets
    providers/                   # Riverpod state management
    widgets/                     # Reusable components
```

## Adding a Feature

1. Define entity in `domain/entities/`
2. Define model in `data/models/` (with `fromJson`/`toJson`)
3. Define repository interface in `domain/repositories/`
4. Implement remote datasource in `data/datasources/`
5. Implement repository in `data/repositories/`
6. Define use case in `domain/usecases/`
7. Create provider in `presentation/providers/`
8. Add Wire provider in `repository_providers.dart`
9. Create/update page in `presentation/pages/`
10. Create/update widgets in `presentation/widgets/`
11. Add navigation in `home_page.dart` if needed
12. Write tests

## Code Style

- Strict typing with non-nullable by default
- Immutable state classes with `copyWith`
- `Equatable` for entity equality
- Named constructors for models (`fromJson`, `fromEntity`)
- `Result<T>` for operation outcomes (Success/Failure union)
- `Semantics` wrappers for accessibility

## State Management Rules

- UI reads state via `ref.watch(provider)`
- UI triggers actions via `ref.read(provider.notifier).action()`
- Complex state uses `StateNotifier` with `copyWith`
- Simple values use `Provider`
- Streams use `StreamProvider`

## Testing

```bash
# Run unit tests
flutter test test/unit/

# Run widget tests
flutter test test/widget/

# Run all tests
flutter test
```

## Build

```bash
# Android
flutter build apk --release

# iOS
flutter build ios --release
```
