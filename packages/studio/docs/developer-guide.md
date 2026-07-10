# Developer Guide

## Project Structure

```
packages/studio/
├── src/
│   ├── app/
│   │   ├── globals.css              # CSS custom properties, theme tokens, animations
│   │   ├── layout.tsx               # Root layout: Inter font, ThemeProvider, metadata
│   │   ├── page.tsx                 # Landing redirect → /studio/dashboard
│   │   ├── (studio)/
│   │   │   ├── layout.tsx           # Authenticated layout wrapper
│   │   │   └── studio/
│   │   │       ├── page.tsx         # Dashboard
│   │   │       └── {module}/
│   │   │           └── page.tsx     # Workspace module (16 pages)
│   │   └── login/
│   │       └── page.tsx             # Mock auth page
│   ├── components/
│   │   ├── layout/                  # Sidebar, Header, MainLayout, client-layout
│   │   ├── shared/                  # PageHeader, StatCard, DataTable, StatusDot, MetricChart, EmptyState, SectionHeader, LoadingScreen
│   │   └── ui/                      # Button, Card, Badge, Tabs, Dialog, DropdownMenu, Select, Switch, Input, Progress, Separator, Tooltip, Avatar, ScrollArea
│   ├── hooks/                       # (reserved for custom hooks)
│   ├── lib/
│   │   ├── api.ts                   # Gateway API client
│   │   └── utils.ts                 # cn() helper (clsx + tailwind-merge)
│   ├── stores/
│   │   ├── app-store.ts             # Global app state (auth, workspace, sidebar, health)
│   │   └── ui-store.ts             # Workspace UI state (active panels, selected items)
│   └── types/
│       └── index.ts                 # All TypeScript interfaces
├── public/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

## Adding a New Workspace Page

1. Create directory: `src/app/(studio)/studio/{module}/`
2. Create `page.tsx` with the page component
3. Add nav section/item to `src/components/layout/sidebar.tsx` `navSections` array
4. Import and register the route in any type definitions if needed

## State Management

Two Zustand stores. No server state lib (React Query, SWR) used.

### app-store.ts

```ts
interface AppState {
  // Auth
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
  logout: () => void;

  // Organization
  workspace: string;
  setWorkspace: (workspace: string) => void;
  organization: Organization | null;
  setOrganization: (org: Organization | null) => void;

  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  // Health
  health: HealthStatus | null;
  setHealth: (health: HealthStatus | null) => void;
}
```

**Pattern:**
- Simple Zustand store with `persist` middleware for sidebar state
- `isAuthenticated` is derived: `get: () => !!get().user`
- Health data is set externally by API calls (no auto-fetch)

### ui-store.ts

```ts
interface UIState {
  // Panels
  activePanel: PanelType | null;
  openPanel: (panel: PanelType) => void;
  closePanel: () => void;

  // Selection
  selectedItem: string | null;
  setSelectedItem: (item: string | null) => void;
  clearSelection: () => void;
}
```

**Pattern:**
- Workspace-level UI state (panel toggles, item selection)
- Imported by workspace pages to manage side panels and selection

## API Client

Located at `src/lib/api.ts`. All requests go through a Gateway URL pattern.

```ts
const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8080";
```

### Methods

```ts
api.dashboard.stats(): Promise<DashboardStats>
api.workspace.list(): Promise<WorkspaceListItem[]>
api.agents.list(): Promise<Agent[]>
api.workflows.list(): Promise<WorkflowDefinition[]>
api.executions.list(): Promise<WorkflowExecution[]>
api.tools.list(): Promise<ToolDefinition[]>
api.extensions.list(): Promise<Extension[]>
api.extensions.available(): Promise<Extension[]>
api.extensions.updates(): Promise<ExtensionUpdate[]>
api.workspaces.get(name: string): Promise<Workspace>
// ... (one method per workspace data type)
```

### Internal Structure

```ts
const api = {
  [module]: {
    [action]: async (params?): Promise<T> => {
      const res = await fetch(`${GATEWAY_URL}/gateway/${path}`);
      if (!res.ok) throw new Error(`API error: ${res.statusText}`);
      return res.json();
    }
  }
};
```

**Pattern:** Module-nested functions, all async with fetch, all throw on non-OK. No axios, no interceptors, no automatic retry.

### Gateway URL

The `NEXT_PUBLIC_GATEWAY_URL` environment variable configures the Service Gateway endpoint. Defaults to `http://localhost:8080`.

## Authentication

- **Auth flow**: Mock login page at `src/app/login/page.tsx` — email/password form with hardcoded user
- **Session**: Auth state stored in Zustand (not cookies/tokens)
- **Layout guard**: `(studio)/layout.tsx` checks `isAuthenticated`, redirects to `/login` if false
- **Protected routes**: All `/studio/*` pages are behind the authenticated layout

## TypeScript Types

Defined in `src/types/index.ts`. Key categories:

| Category | Types |
|---|---|
| Auth | `User`, `Organization` |
| Workspace | `Workspace`, `Project`, `Environment` |
| Agents | `Agent`, `Capability`, `AgentHealth` |
| Workflows | `WorkflowDefinition`, `Node`, `Connection`, `WorkflowExecution` |
| Tools | `ToolDefinition`, `ToolPermission`, `ToolExecution` |
| Extensions | `Extension`, `ExtensionUpdate` |
| Infrastructure | `InfraComponent`, `InfraHealth` |
| Observability | `MetricPoint`, `LogEntry`, `TraceData`, `Alert` |
| Events | `EventData` |
| Security | `UserRole`, `SecurityPolicy`, `AuditEntry` |
| AI Runtime | `AIProvider`, `AIModel`, `TokenUsage` |
| Config | `FeatureFlag`, `ConfigEntry`, `ConfigProfile` |
| Knowledge | `Collection`, `Document`, `KnowledgeEntry` |
| Memory | `MemoryEntry`, `MemoryCategory`, `MemoryPolicy` |
| API Explorer | `APIEndpoint` |
| Monitoring | `Metric`, `MonitorLog`, `Trace`, `Alert` |
| Dashboard | `DashboardStats` |
| General | `HealthStatus`, `ComponentHealth`, `NavSection`, `NavItem` |

## Mock Data

All workspace pages use hardcoded mock data arrays and objects defined inline in each `page.tsx`. There is no centralized mock data factory. This is intentional for the prototype phase.

To connect to a real backend:
1. Replace mock data with `useEffect` + `api.module.action()` calls
2. Add loading states (LoadingScreen)
3. Add error states
4. Remove mock data constants

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_GATEWAY_URL` | `http://localhost:8080` | Service Gateway endpoint |

## Linting & Formatting

- Uses Next.js ESLint config (`next/core-web-vitals`)
- TypeScript strict mode enabled in `tsconfig.json`
- `tailwindcss-animate` plugin for Tailwind + Framer Motion compatibility

## Build & Run

```bash
# Development
npm run dev          # Starts Next.js dev server

# Build
npm run build        # Production build

# Lint
npm run lint         # ESLint check
```

## Package Dependencies (Key)

| Package | Purpose |
|---|---|
| `next` (14.2.x) | Framework |
| `react` / `react-dom` (18.x) | UI library |
| `typescript` (5.x) | Type system |
| `tailwindcss` (3.x) | Utility CSS |
| `zustand` (4.x) | State management |
| `framer-motion` (11.x) | Animations |
| `lucide-react` | Icon library |
| `recharts` (2.x) | Charts |
| `@radix-ui/*` | Accessible UI primitives |
| `class-variance-authority` | Component variants |
| `clsx` + `tailwind-merge` | className merging |
| `next-themes` | Theme toggling |
| `@xyflow/react` | Workflow designer (future) |
