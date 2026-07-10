# Agent Platform Architecture

## Overview

The Agent Platform is a production-grade, protocol-based architecture for creating, managing, coordinating, supervising, and retiring specialized autonomous agents within the JARVIS AI Ecosystem. It follows Clean Architecture, Domain-Driven Design, and SOLID principles — fully decoupled from infrastructure, frameworks, and external dependencies.

## Core Principles

1. **Protocol over Inheritance** — All contracts are defined as `typing.Protocol` classes, enabling structural subtyping and loose coupling.
2. **In-Memory First** — Every component ships with a fully functional in-memory default implementation for development, testing, and single-process deployments.
3. **Contract-Based Communication** — Agents never call each other directly; they communicate through the `CommunicationBus` using requests, responses, and events identified by correlation IDs.
4. **Layered Permissions** — All access is governed by a hierarchical permission model (`NONE < READ < WRITE < ADMIN`) with scope isolation.
5. **Lifecycle Governance** — Every agent follows a strictly enforced state machine with valid transitions only.
6. **Policy-Driven** — Behavior is governed by configurable policies resolved by scope (owner, workspace, project).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        AgentKernel                          │
│  Central coordinator — facades all subsystems               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Registry │  │ Lifecycle    │  │ Capability Manager   │   │
│  │          │  │ Manager      │  │                      │   │
│  └──────────┘  └──────────────┘  └──────────────────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Permission│  │ Goal         │  │ Task Manager         │   │
│  │ Manager  │  │ Manager      │  │                      │   │
│  └──────────┘  └──────────────┘  └──────────────────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Comm.    │  │ Memory       │  │ Knowledge            │   │
│  │ Bus      │  │ Interface    │  │ Interface            │   │
│  └──────────┘  └──────────────┘  └──────────────────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Tool     │  │ Health       │  │ Policy Engine        │   │
│  │ Interface│  │ Monitor      │  │                      │   │
│  └──────────┘  └──────────────┘  └──────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **AgentKernel** | Central facade that orchestrates all subsystems |
| **Registry** | Stores and retrieves agent metadata |
| **LifecycleManager** | Governs state transitions (state machine) |
| **CapabilityManager** | Discovers agents by capability |
| **PermissionManager** | Evaluates hierarchical access control |
| **GoalManager** | Creates and tracks high-level goals |
| **TaskManager** | Manages task lifecycle with retry logic |
| **CommunicationBus** | Mediates all inter-agent messaging |
| **MemoryInterface** | Per-agent key-value storage |
| **KnowledgeInterface** | Document storage and search |
| **ToolInterface** | Tool registration and access control |
| **HealthMonitor** | Heartbeat tracking, failure detection |
| **PolicyEngine** | Resolves and evaluates configurable policies |

## Layered Architecture

```
┌─────────────────────────────────────┐
│         Domain Models               │
│  (AgentMetadata, AgentTask, etc.)   │
├─────────────────────────────────────┤
│         Protocols (Contracts)       │
│  (AgentRegistry, TaskManager, etc.) │
├─────────────────────────────────────┤
│      Default Implementations        │
│  (InMemory* classes)                │
├─────────────────────────────────────┤
│         AgentKernel                 │
│  (Facade / Coordinator)             │
└─────────────────────────────────────┘
```

## Extensibility

Each protocol can be backed by any implementation (database, API, cloud service) without changes to the kernel or other components — as long as the contract is satisfied.
