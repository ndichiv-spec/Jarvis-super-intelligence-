# Enterprise Platform Architecture Summary

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                       ENTERPRISE PLATFORM KERNEL                        │
│                    (EnterprisePlatform orchestrator)                     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │  ORG     │ │WORKSPACE │ │  USER    │ │GOVERNANCE│ │COLLAB    │     │
│  │ MGMT    │ │ ADMIN    │ │ ADMIN    │ │          │ │          │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ SECURITY │ │OBSERVABI │ │ RESOURCE │ │ BILLING  │ │COMPLIANCE│     │
│  │ CENTER   │ │ -LITY    │ │ MGMT     │ │          │ │          │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │INTEGRAT'N│ │ ADMIN    │ │ANALYTICS │ │CONTINUITY│                    │
│  │ HUB      │ │ PORTAL   │ │          │ │          │                    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                    │
└────────────────────────────────────────────────────────────────────────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ jarvis-  │    │ jarvis-  │     │ jarvis-  │     │ jarvis-  │
   │ security │    │  core    │     │  infra   │     │  cloud   │
   └──────────┘    └──────────┘     └──────────┘     └──────────┘
```

## Core Design Patterns

### 1. Protocol-Based Repository Pattern
All persistence abstractions use `Protocol` classes, enabling in-memory testing and production backends:

```
Service ──▶ Repository(Protocol) ◀── InMemoryRepo / SQLRepo / CloudRepo
```

### 2. Immutable Domain Models
All entities use `@dataclass(frozen=True, slots=True)` for thread-safe, memory-efficient state.

### 3. Constructor Injection
Services receive repositories via constructors — no global state, no service locator.

### 4. Multi-Tenant Isolation
Every repository method filters by `org_id` and/or `workspace_id` to guarantee tenant isolation.

## Data Model Relationships

```
Organization (1)
  ├── OrgUnits (N) — hierarchical tree (division → department → team)
  ├── Members (N) — users with roles
  ├── Workspaces (N)
  │     ├── Projects (N)
  │     ├── Members (N)
  │     ├── ResourceAllocations (N)
  │     └── SharedProjects (N) [collaboration]
  ├── Policies (N) [governance]
  ├── SecurityIncidents (N)
  ├── RiskReports (N)
  ├── Subscriptions (1) [billing]
  ├── Licenses (1)
  └── Adapters (N) [integration]

Global
  └── Policies (N) — apply to all organizations
```

## Service Composition

The `EnterprisePlatform` kernel composes all 14 services, providing:
- A single entry point for enterprise operations
- Consistent lifecycle management
- Unified health reporting
- Clear dependency graph

## Integration Architecture

```
External Systems  ──▶ IntegrationAdapter(s)  ──▶ IntegrationHubService
                         │
                     (capability-based routing)
                         │
                    ┌────┴────┐
                    │         │
               JARVIS     External
               Services   Services
```

## Key Metrics

- **14 domain modules**
- **9 repository protocols**
- **50+ domain models**
- **80+ service methods**
- **123 automated tests**
- **8 documentation guides**
