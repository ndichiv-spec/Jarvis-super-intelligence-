# Extension Manifest Specification

## Overview

The `ExtensionManifest` is the canonical description of an extension. It declares identity, metadata, capabilities, dependencies, permissions, and platform compatibility constraints. All extensions — both built-in and third-party — are defined via manifests.

## Manifest Fields

```python
@dataclass(frozen=True, slots=True)
class ExtensionManifest:
    extension_id: str                        # Unique identifier (e.g., "jarvis.builtin.tool_pack")
    name: str                                # Human-readable name
    version: VersionInfo                     # Semantic version
    publisher: str = ""                      # Publisher name
    description: str = ""                    # Description of the extension
    license: str = ""                        # License identifier
    capabilities: tuple[CapabilityDefinition, ...] = ()
    dependencies: tuple[DependencyDefinition, ...] = ()
    permissions: tuple[PermissionRequest, ...] = ()
    min_platform_version: VersionInfo = VersionInfo(0,0,0)
    max_platform_version: VersionInfo | None = None
    extension_type: ExtensionType = ExtensionType.TOOL_PACK
    tags: tuple[str, ...] = ()
```

## Field Requirements

| Field | Required | Validation |
|-------|----------|------------|
| `extension_id` | Yes | Must be non-empty string |
| `name` | Yes | Must be non-empty string |
| `version` | Yes | Must not be `0.0.0` |
| `publisher` | No | Empty string if not set |
| `capabilities` | No | Duplicate `identifier` values rejected |

## Extension Types

| Type | Description |
|------|-------------|
| `AI_PROVIDER` | Registers AI model provider connectors |
| `KNOWLEDGE_CONNECTOR` | Connects to external knowledge sources |
| `TOOL_PACK` | Registers tool collections for the Tool Platform |
| `AUTOMATION_PACK` | Provides workflow templates and automation patterns |
| `UI_MODULE` | Contributes user interface components |
| `VOICE` | Adds voice input/output capabilities |
| `VISION` | Adds image/video processing capabilities |
| `ENTERPRISE_INTEGRATION` | Provides enterprise system integration connectors |

## Capability Definition

```python
@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    capability_type: CapabilityType    # TOOL, AGENT, AI_PROVIDER, WORKFLOW_TEMPLATE, etc.
    identifier: str                    # Unique capability identifier
    name: str                          # Human-readable name
    description: str = ""              # Description
    version: VersionInfo = VersionInfo() # Capability version
```

### Capability Types

- `TOOL` — Contributes executable tools
- `AGENT` — Contributes AI agents
- `AI_PROVIDER` — Contributes model provider access
- `WORKFLOW_TEMPLATE` — Contributes automation workflow templates
- `KNOWLEDGE_CONNECTOR` — Contributes knowledge source connectors
- `UI_COMPONENT` — Contributes reusable UI components
- `INTEGRATION` — Contributes system integrations
- `SERVICE` — Contributes background services
- `COMMAND` — Contributes executable commands
- `EVENT_HANDLER` — Contributes event-driven handlers

## Dependency Definition

```python
@dataclass(frozen=True, slots=True)
class DependencyDefinition:
    extension_id: str                  # ID of required extension
    version_constraint: str = ">=0.0.0"  # Semver constraint
    dependency_type: DependencyType = DependencyType.REQUIRED  # REQUIRED or OPTIONAL
```

## Permission Request

```python
@dataclass(frozen=True, slots=True)
class PermissionRequest:
    permission_scope: PermissionScope  # What is being requested
    reason: str = ""                   # Justification
    required: bool = True              # Whether permission is mandatory
```

## VersionInfo

```python
@dataclass(frozen=True, slots=True)
class VersionInfo:
    major: int = 0
    minor: int = 0
    patch: int = 0
    pre_release: str | None = None     # e.g., "beta.1", "rc1"
    build_metadata: str | None = None  # e.g., "build42"
```

Parsing: `VersionInfo.parse("1.2.3-beta.1+build42")` → `major=1, minor=2, patch=3, pre_release="beta.1", build_metadata="build42"`.

## Example Manifest

```python
ExtensionManifest(
    extension_id="mycorp.search_tools",
    name="Search Tool Pack",
    version=VersionInfo(1, 2, 0),
    publisher="MyCorp",
    description="Advanced search tool collection",
    extension_type=ExtensionType.TOOL_PACK,
    capabilities=(
        CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="mycorp.cap.web_search",
            name="Web Search",
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
            reason="Register search tools",
        ),
    ),
    min_platform_version=VersionInfo(11, 0, 0),
)
```
