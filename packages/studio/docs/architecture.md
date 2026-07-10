# JARVIS Studio Architecture

## Overview

JARVIS Studio is a Next.js 14 single-page application (SPA) that serves as the engineering command center for the JARVIS AI Ecosystem. It provides workspace management, agent design, workflow orchestration, knowledge management, observability, and platform administration through a unified UI.

The Studio follows a **strict three-tier architecture** with no business logic in the frontend:

```
┌──────────────────────────────────────────────────────────┐
│                     JARVIS Studio UI                      │
│  (Next.js 14 / React 18 / TypeScript / Tailwind CSS)      │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Sidebar  │  │   Workspace  │  │  Shared Components │  │
│  │  Header   │  │   Pages x16  │  │  (DataTable,       │  │
│  │  Layout   │  │              │  │   StatCard, etc.)   │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│         │              │                    │             │
│         ▼              ▼                    ▼             │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Zustand State Stores                 │    │
│  │  ┌─────────────────┐  ┌────────────────────────┐ │    │
│  │  │   App Store      │  │     UI Store            │ │    │
│  │  │ (theme, user,    │  │ (panels, console tab,   │ │    │
│  │  │  sidebar, stats) │  │  selection state)       │ │    │
│  │  └─────────────────┘  └────────────────────────┘ │    │
│  └──────────────────────────────────────────────────┘    │
│                          │                                │
│                          ▼                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │              API Client (lib/api.ts)              │    │
│  │  Single entry point → fetchApi() via Gateway      │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│            Service Gateway (port 8000)                    │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐ │
│  │  Auth   │ │  Router  │ │  Rate  │ │  Aggregator   │ │
│  │  Proxy  │ │          │ │ Limit  │ │  (compose      │ │
│  │         │ │          │ │        │ │   responses)   │ │
│  └─────────┘ └──────────┘ └────────┘ └───────────────┘ │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│              Backend Microservices                        │
│  ┌────────┐┌────────┐┌────────┐┌────────┐┌───────────┐ │
│  │ Agent  ││Workflow││ Tool   ││Memory  ││ Knowledge  │ │
│  │ Service││Service ││Service ││Service ││  Service   │ │
│  └────────┘└────────┘└────────┘└────────┘└───────────┘ │
│  ┌────────┐┌────────┐┌────────┐┌────────┐┌───────────┐ │
│  │Security││Infra   ││Observ- ││AI      ││ Config     │ │
│  │Service ││Service ││ability ││Runtime ││  Service   │ │
│  └────────┘└────────┘└────────┘└────────┘└───────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Action → React Component → Zustand Store → API Client → Gateway → Backend
     ↑                                                                    │
     └──────────────────── Response ← JSON ←──────────────────────────────┘
```

1. **User Action** — Click, form input, navigation
2. **React Component** — Page or shared component handles the event
3. **Zustand Store** — App store (global state) or UI store (workspace-local state)
4. **API Client** — `api.ts` constructs a fetch to `{GATEWAY_URL}/gateway/{path}`
5. **Service Gateway** — Proxies, authenticates, rate-limits, and routes to backend
6. **Backend** — Returns typed JSON; store updates propagate via React bindings

## Module Dependencies

```
src/
├── app/                    # Next.js App Router pages (16 workspace pages + layout)
│   ├── layout.tsx          # Root layout (fonts, metadata)
│   ├── client-layout.tsx   # Theme hydration + loading screen
│   ├── globals.css         # Design tokens (light/dark)
│   └── studio/             # All workspace pages
│       ├── page.tsx                # Dashboard
│       ├── workspace/page.tsx      # Workspace Manager
│       ├── agents/page.tsx         # Agent Designer
│       ├── workflows/page.tsx      # Workflow Designer
│       ├── tools/page.tsx          # Tool Manager
│       ├── extensions/page.tsx     # Extension Manager
│       ├── knowledge/page.tsx      # Knowledge Explorer
│       ├── memory/page.tsx         # Memory Inspector
│       ├── automation/page.tsx     # Automation Monitor
│       ├── events/page.tsx         # Event Monitor
│       ├── ai/page.tsx             # AI Runtime Manager
│       ├── security/page.tsx       # Security Center
│       ├── infrastructure/page.tsx # Infrastructure Monitor
│       ├── observability/page.tsx  # Observability Center
│       ├── api-explorer/page.tsx   # API Explorer
│       ├── config/page.tsx         # Configuration Center
│       └── console/page.tsx        # Developer Console
├── components/
│   ├── layout/             # Sidebar, Header, MainLayout
│   ├── shared/             # DataTable, StatCard, StatusDot, MetricChart, etc.
│   └── ui/                 # Primitives (Button, Card, Badge, Tabs, etc.)
├── stores/
│   ├── app-store.ts        # Global app state (Zustand)
│   └── ui-store.ts         # Workspace-local UI state (Zustand)
├── lib/
│   ├── api.ts              # Gateway API client
│   └── utils.ts            # cn(), formatRelativeTime(), truncate(), etc.
├── types/
│   └── index.ts            # All TypeScript interfaces (386 lines)
└── hooks/                  # (reserved for custom hooks)
```

## Key Design Decisions

### 1. No Business Logic in Frontend

The frontend is a pure presentation layer. All business logic, validation, orchestration, and data transformation lives in backend services accessed exclusively through the Service Gateway. The Studio does not perform any of the following client-side:
- Data validation beyond basic form hygiene
- Workflow execution or state management
- Security policy enforcement
- AI model inference or routing decisions
- Persistent data mutation outside optimistic UI updates

### 2. Service Gateway Integration Only

All data flows through `api.ts` which targets a single gateway URL (`NEXT_PUBLIC_GATEWAY_URL`). The gateway handles:
- Authentication and authorization
- Rate limiting
- Request routing to appropriate microservices
- Response aggregation and composition
- Error normalization

No page or component directly calls backend microservices.

### 3. Zustand for State Management

Two lightweight Zustand stores replace a heavier solution like Redux:
- **App Store** — Global cross-cutting state (theme, user, sidebar, workspace metadata, loading)
- **UI Store** — Workspace-local UI state (open panels, selected nodes/edges, console tab)

### 4. Shared Component Library

All pages compose from a consistent set of shared components (`DataTable`, `StatCard`, `StatusDot`, `MetricChart`, `PageHeader`, `SectionHeader`, `EmptyState`, `LoadingScreen`) and UI primitives (`Button`, `Card`, `Badge`, `Tabs`, `Dialog`, etc.) built on Radix UI primitives and styled with class-variance-authority.

### 5. Staggered Animation System

Every workspace page uses a consistent Framer Motion pattern with `containerVariants` (staggerChildren: 0.04) and `itemVariants` for fade-in-up entrance animations, providing a unified feel without per-page animation logic.

### 6. Dark Mode via CSS Custom Properties

Theme switching uses CSS custom properties (HSL values) toggled via the `.dark` class on `<html>`, avoiding runtime stylesheet injection. The `font-size` and `reducedMotion` preferences also live in `UserPreferences` for future implementation.
