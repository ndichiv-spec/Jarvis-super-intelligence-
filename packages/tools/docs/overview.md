# Tool Platform — Overview

The JARVIS Tool Platform provides a secure, extensible, provider-independent
framework for registering, discovering, validating, executing, monitoring, and
governing tools used by the JARVIS Brain and Agent Platform.

## Core Concepts

- **ToolDefinition** — immutable contract defining a tool's identity, schema,
  permissions, and execution policy.
- **ToolKernel** — central coordinator that wires all subsystems together.
- **InMemory Implementations** — fully functional default engines backed by
  in-memory data structures.

## Architecture

```
ToolKernel
  ├── Registry        — register, update, deregister, list tool metadata
  ├── Discovery       — find tools by identifier, category, capability, workspace, or query
  ├── Validation      — validate inputs, outputs, permissions, and execution policies
  ├── Execution       — manage tool execution lifecycle (queue → run → complete/fail)
  │   └── Executor    — pluggable per-tool execution logic
  ├── Permissions     — grant, revoke, check hierarchical access (NONE < READ < WRITE < ADMIN)
  ├── Policy          — register, resolve, and evaluate governance policies
  └── Health          — track execution metrics and surface unhealthy tools
```

## Design Principles

- **No external dependencies** — pure Python with zero framework/LLM/infrastructure coupling.
- **Protocol-based** — all subsystems defined as `typing.Protocol` interfaces.
- **Immutable contracts** — `ToolDefinition` is a frozen dataclass; state transitions
  produce new instances.
- **Lifecycle management only** — the platform manages *when* and *how* a tool runs,
  not *what* it does internally.
