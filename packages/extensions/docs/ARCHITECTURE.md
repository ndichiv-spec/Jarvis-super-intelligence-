# Extension Platform Architecture

## Overview

The JARVIS Extension Platform provides a production-grade architecture for managing extensions — plugins that extend the JARVIS AI Ecosystem with new capabilities. The platform handles the full lifecycle: discovery, installation, verification, activation, update, and removal of extensions.

## Design Principles

- **Protocol-based**: All subsystem contracts are defined as Python `Protocol` classes, enabling multiple interchangeable implementations.
- **Domain-driven**: Core domain models (manifests, metadata, capabilities, permissions) are isolated from infrastructure concerns.
- **Strict state machine**: Extension lifecycle is governed by a rigorous state transition map — invalid transitions raise `ValueError`.
- **Zero external dependencies**: Pure Python 3.13+ implementation with no dependencies on databases, message queues, or external services.
- **Dependency inversion**: High-level kernel coordinates subsystems through protocol interfaces; concrete implementations are injected at construction.

## Subsystem Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ExtensionKernel                          │
│  (Central coordinator — wires all subsystems together)      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Registry │  │ Manifest │  │Dependency│  │Compat    │    │
│  │          │  │Validator │  │Manager   │  │Engine    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │Capability│  │Lifecycle │  │Permission│  │Isolation │    │
│  │Registry  │  │Manager   │  │Manager   │  │Manager   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Version  │  │  Health  │  │  Event   │                   │
│  │ Manager  │  │ Monitor  │  │Integration│                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### ExtensionKernel (`kernel.py`)
Central coordinator that wires together all 11 subsystems. Exposes high-level operations: `discover`, `install`, `activate`, `deactivate`, `disable`, `enable`, `update`, `remove`, along with query methods `get_metadata`, `list_extensions`, `get_health`.

### ExtensionRegistry (`registry.py`)
Stores extension metadata in memory. Supports CRUD operations and filtered listing by status or type.

### ManifestValidator (`manifest.py`)
Validates extension manifests at discovery time: checks for empty IDs, empty names, unset versions (`0.0.0`), and duplicate capability identifiers.

### DependencyManager (`dependency.py`)
Resolves dependencies by checking that required extensions exist and satisfy version constraints. Detects circular dependency chains via DFS traversal.

### CompatibilityEngine (`compatibility.py`)
Checks platform version compatibility (min/max bounds), version constraint satisfaction, and capability contract compatibility between providers and consumers.

### CapabilityRegistry (`capabilities.py`)
Tracks what capabilities each extension provides. Allows registration, lookup, type-filtered listing, and bulk removal per extension.

### LifecycleManager (`lifecycle.py`)
Strict state machine governing extension lifecycle transitions. See [LIFECYCLE.md](LIFECYCLE.md) for the full transition diagram.

### PermissionManager (`permissions.py`)
Manages granted permissions per extension. Supports grant, revoke, check, list, and revoke-all operations.

### IsolationManager (`isolation.py`)
Manages isolation policies (sandbox configuration, resource limits, capability allow/deny lists). The platform defines the contract and preparation hooks; sandbox execution is deferred to infrastructure.

### VersionManager (`version.py`)
Version comparison, constraint checking, upgrade suggestion, and deprecation detection.

### HealthMonitor (`health.py`)
Tracks activation/failure counts, health status, and error messages for each extension.

### EventIntegration (`events.py`)
Manages event subscription contracts — extensions can subscribe to named event types with handler identifiers.

## Package Structure

```
packages/extensions/
├── pyproject.toml
├── src/
│   ├── jarvis/
│   │   └── extensions/          # Namespace package
│   │       └── __init__.py
│   └── jarvis_extensions/       # Main package
│       ├── __init__.py           # Public API exports
│       ├── models.py             # Domain types (enums, dataclasses)
│       ├── protocols.py          # Protocol interfaces
│       ├── kernel.py             # ExtensionKernel coordinator
│       ├── registry.py           # InMemoryExtensionRegistry
│       ├── manifest.py           # InMemoryManifestValidator
│       ├── dependency.py         # InMemoryDependencyManager
│       ├── compatibility.py      # InMemoryCompatibilityEngine
│       ├── capabilities.py       # InMemoryCapabilityRegistry
│       ├── lifecycle.py          # InMemoryLifecycleManager
│       ├── permissions.py        # InMemoryPermissionManager
│       ├── isolation.py          # InMemoryIsolationManager
│       ├── version.py            # InMemoryVersionManager
│       ├── health.py             # InMemoryHealthMonitor
│       ├── events.py             # InMemoryEventIntegration
│       └── builtins.py           # BUILT_IN_EXTENSIONS definitions
├── tests/
│   └── test_extension_platform.py
└── docs/
    ├── ARCHITECTURE.md
    ├── LIFECYCLE.md
    ├── MANIFEST.md
    ├── COMPATIBILITY.md
    ├── DEPENDENCY.md
    ├── PERMISSION.md
    ├── DEVELOPER_GUIDE.md
    └── EXTENSION_AUTHOR_GUIDE.md
```
