# Developer Guide

## Getting Started

The Extension Platform is a pure Python package with zero external dependencies.

```bash
cd packages/extensions
uv pip install -e .
```

## Package API

All public types and implementations are exported from `jarvis_extensions`:

```python
from jarvis_extensions import (
    ExtensionKernel,
    ExtensionManifest,
    ExtensionMetadata,
    ExtensionStatus,
    ExtensionType,
    CapabilityDefinition,
    CapabilityType,
    VersionInfo,
    PermissionRequest,
    PermissionScope,
    DependencyDefinition,
    DependencyType,
    IsolationPolicy,
    ResourceLimits,
    InMemoryExtensionRegistry,
    InMemoryManifestValidator,
    InMemoryDependencyManager,
    InMemoryCompatibilityEngine,
    InMemoryCapabilityRegistry,
    InMemoryLifecycleManager,
    InMemoryPermissionManager,
    InMemoryIsolationManager,
    InMemoryVersionManager,
    InMemoryHealthMonitor,
    InMemoryEventIntegration,
    BuiltInExtensionDefinition,
    CompatibilityIssue,
    CompatibilityLevel,
    CompatibilityReport,
    ExtensionHealth,
)
```

## Quick Start

```python
from jarvis_extensions import ExtensionKernel, ExtensionManifest, VersionInfo, CapabilityDefinition, CapabilityType, PermissionRequest, PermissionScope

kernel = ExtensionKernel()

manifest = ExtensionManifest(
    extension_id="my.ext",
    name="My Extension",
    version=VersionInfo(1, 0, 0),
    capabilities=(
        CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="my.cap.tool1",
            name="My Tool",
        ),
    ),
    permissions=(
        PermissionRequest(
            permission_scope=PermissionScope.TOOL_REGISTRATION,
            reason="Register my tools",
        ),
    ),
)

meta = kernel.discover(manifest)     # DISCOVERED
meta = kernel.install("my.ext")      # INSTALLED
meta = kernel.activate("my.ext")     # ACTIVATED
```

## Complete Lifecycle

```python
# Full lifecycle
meta = kernel.discover(manifest)
assert meta.status == ExtensionStatus.DISCOVERED

meta = kernel.install("my.ext")
assert meta.status == ExtensionStatus.INSTALLED

meta = kernel.activate("my.ext")
assert meta.status == ExtensionStatus.ACTIVATED

# Activation registers capabilities
cap = kernel.capability_registry.get_capability("my.cap.tool1")
assert cap is not None

# Deactivate
meta = kernel.deactivate("my.ext")
assert meta.status == ExtensionStatus.PAUSED

# Re-activate
meta = kernel.activate("my.ext")
assert meta.status == ExtensionStatus.ACTIVATED

# Disable (clears caps, permissions, events)
meta = kernel.disable("my.ext")
assert meta.status == ExtensionStatus.DISABLED

# Re-enable
meta = kernel.enable("my.ext")
assert meta.status == ExtensionStatus.ACTIVATED

# Remove (terminal)
removed = kernel.remove("my.ext")
assert removed.status == ExtensionStatus.REMOVED
assert kernel.get_metadata("my.ext") is None
```

## Update

```python
kernel.discover(manifest)
kernel.install("my.ext")

new_manifest = ExtensionManifest(
    extension_id="my.ext",
    name="My Extension v2",
    version=VersionInfo(1, 1, 0),
)
meta = kernel.update("my.ext", new_manifest)
assert meta.manifest.version == VersionInfo(1, 1, 0)
assert meta.status == ExtensionStatus.VERIFIED
```

## Working with Built-in Extensions

```python
from jarvis_extensions.builtins import BUILT_IN_EXTENSIONS

for ext_def in BUILT_IN_EXTENSIONS:
    manifest = ExtensionManifest(
        extension_id=ext_def.extension_id,
        name=ext_def.name,
        version=ext_def.version,
        publisher=ext_def.publisher,
        description=ext_def.description,
        extension_type=ext_def.extension_type,
        capabilities=ext_def.capabilities,
        permissions=ext_def.permissions,
        dependencies=ext_def.dependencies,
    )
    kernel.discover(manifest)
```

## Customizing Subsystems

Each subsystem can be replaced with a custom implementation by implementing its protocol interface:

```python
from jarvis_extensions.protocols import LifecycleManager
from jarvis_extensions.models import ExtensionMetadata, ExtensionStatus

class CustomLifecycleManager:
    def transition(self, metadata: ExtensionMetadata, target: ExtensionStatus) -> ExtensionMetadata: ...
    def can_transition(self, current: ExtensionStatus, target: ExtensionStatus) -> bool: ...
    def valid_transitions(self, current: ExtensionStatus) -> tuple[ExtensionStatus, ...]: ...

kernel = ExtensionKernel()
kernel.lifecycle = CustomLifecycleManager()
```

## Testing

```bash
cd packages/extensions
pytest tests/ -v

# With coverage
pytest tests/ --cov=jarvis_extensions --cov-report=term-missing
```
