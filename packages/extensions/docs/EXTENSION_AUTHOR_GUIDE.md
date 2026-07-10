# Extension Author Guide

## Writing an Extension

An extension is defined by its `ExtensionManifest`. The manifest declares everything the platform needs to know: identity, capabilities, dependencies, permissions, and platform compatibility.

## Step-by-Step

### 1. Choose an Extension Type

| Type | When to Use |
|------|-------------|
| `AI_PROVIDER` | Adding a new model provider (OpenAI, Anthropic, etc.) |
| `KNOWLEDGE_CONNECTOR` | Connecting to external knowledge bases |
| `TOOL_PACK` | Publishing a collection of reusable tools |
| `AUTOMATION_PACK` | Providing workflow templates |
| `UI_MODULE` | Contributing UI components |
| `VOICE` | Adding speech capabilities |
| `VISION` | Adding image/video processing |
| `ENTERPRISE_INTEGRATION` | Integrating with enterprise systems (LDAP, SAML, etc.) |

### 2. Define Your Manifest

```python
from jarvis_extensions import (
    ExtensionManifest,
    VersionInfo,
    ExtensionType,
    CapabilityDefinition,
    CapabilityType,
    DependencyDefinition,
    PermissionRequest,
    PermissionScope,
)

manifest = ExtensionManifest(
    extension_id="com.example.my_extension",
    name="My Example Extension",
    version=VersionInfo(1, 0, 0),
    publisher="Example Corp",
    description="Does something useful in the JARVIS ecosystem",
    license="MIT",
    extension_type=ExtensionType.TOOL_PACK,
    capabilities=(
        CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="com.example.cap.my_tool",
            name="My Tool",
            description="A useful tool",
            version=VersionInfo(1, 0, 0),
        ),
    ),
    dependencies=(
        DependencyDefinition(
            extension_id="jarvis.builtin.tool_pack",
            version_constraint=">=1.0.0",
        ),
    ),
    permissions=(
        PermissionRequest(
            permission_scope=PermissionScope.TOOL_REGISTRATION,
            reason="Register my tools with the platform",
            required=True,
        ),
    ),
    min_platform_version=VersionInfo(11, 0, 0),
    tags=("example", "tutorial"),
)
```

### 3. Register with the Kernel

```python
from jarvis_extensions import ExtensionKernel

kernel = ExtensionKernel()
meta = kernel.discover(manifest)
meta = kernel.install(manifest.extension_id)
meta = kernel.activate(manifest.extension_id)
```

### 4. Declare Capabilities

Capabilities are the unit of functionality your extension provides. Each capability has a type and a unique identifier.

```python
CapabilityDefinition(
    capability_type=CapabilityType.TOOL,
    identifier="com.example.cap.search",
    name="Advanced Search",
    description="Performs intelligent search across knowledge sources",
)
```

### 5. Declare Dependencies

If your extension depends on another extension's capabilities, declare a dependency:

```python
DependencyDefinition(
    extension_id="jarvis.builtin.knowledge_connectors",
    version_constraint="^1.0.0",       # caret: compatible with 1.x
    dependency_type=DependencyType.REQUIRED,
)
```

**Constraint Operators:**
- `>=1.0.0` — minimum version
- `^1.0.0` — compatible with same major version
- `~1.2.0` — same major & minor, patch >=
- `==1.0.0` — exact version
- `>1.0.0`, `<2.0.0`, `<=1.5.0` — comparison

### 6. Request Permissions

Declare what permissions your extension needs:

```python
PermissionRequest(
    permission_scope=PermissionScope.KNOWLEDGE_ACCESS,
    reason="Read knowledge sources to provide search results",
    required=True,
)
```

### 7. Platform Compatibility

Set your minimum and (optionally) maximum supported platform version:

```python
ExtensionManifest(
    ...
    min_platform_version=VersionInfo(11, 0, 0),
    max_platform_version=VersionInfo(12, 0, 0),  # optional
)
```

## Best Practices

1. **Use reverse-domain identifiers**: `com.yourcompany.extension_id` to avoid namespace collisions.
2. **Be specific with versions**: Don't use `>=0.0.0` unless truly independent of all other extensions.
3. **Document permissions**: Always provide a clear `reason` string explaining why each permission is needed.
4. **Set min_platform_version**: Declare the minimum JARVIS platform version your extension requires.
5. **Prefer `^` constraints**: Caret constraints (`^1.0.0`) allow compatible updates while preventing breaking changes.
6. **Avoid pinned dependencies**: `==` constraints trigger a `DEPRECATED` compatibility warning.

## Built-in Extensions

The platform includes 8 built-in extensions. Your extension can depend on them:

| ID | Type |
|----|------|
| `jarvis.builtin.ai_providers` | AI_PROVIDER |
| `jarvis.builtin.knowledge_connectors` | KNOWLEDGE_CONNECTOR |
| `jarvis.builtin.tool_pack` | TOOL_PACK |
| `jarvis.builtin.automation_pack` | AUTOMATION_PACK |
| `jarvis.builtin.ui_module` | UI_MODULE |
| `jarvis.builtin.voice` | VOICE |
| `jarvis.builtin.vision` | VISION |
| `jarvis.builtin.enterprise` | ENTERPRISE_INTEGRATION |

## Isolation Policies (Advanced)

Extensions can declare isolation requirements:

```python
from jarvis_extensions import IsolationPolicy, ResourceLimits, CapabilityType

policy = IsolationPolicy(
    sandbox_enabled=True,
    resource_limits=ResourceLimits(
        max_memory_mb=256,
        max_cpu_percent=50,
        max_concurrent_tasks=4,
    ),
    allowed_capabilities=(CapabilityType.TOOL,),
    denied_capabilities=(CapabilityType.AGENT,),
)
```

## Migration from Previous Versions

When updating your extension:
1. Increment the version number.
2. Call `kernel.update("ext_id", new_manifest)` to transition through `UPDATING → VERIFIED`.
3. Then `kernel.activate("ext_id")` to resume full operation.
