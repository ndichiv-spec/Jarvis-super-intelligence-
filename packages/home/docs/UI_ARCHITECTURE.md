# JARVIS Home — UI Architecture

## Technology Stack & Rationale

| Technology | Purpose | Rationale |
|---|---|---|
| **Next.js 14** (App Router) | React framework | File-based routing, server components, streaming SSR |
| **React 18** | UI library | Concurrent features, `use client` boundaries |
| **TypeScript 5** | Type safety | Strict mode, full type coverage across all modules |
| **Tailwind CSS 3** | Utility-first styling | Rapid prototyping, consistent design tokens via `tailwind.config.ts` |
| **Framer Motion 11** | Animation | Declarative `motion` components, layout animations, `AnimatePresence` |
| **Zustand 4** | State management | Minimal boilerplate, no providers, `create` + hook pattern |
| **Radix UI** (14 primitives) | Headless components | Accessible, unstyled, composable (Dialog, Dropdown, Tooltip, Tabs, etc.) |
| **Lucide React** | Icon library | Consistent SVG icon set, tree-shakeable |
| **Recharts 2** | Charts | Lightweight charting for MetricChart component |
| **clsx + tailwind-merge** | Class merging | `cn()` utility for conditional Tailwind classes |
| **class-variance-authority** | Variants | Component variant management (future use) |

### Rationale

Next.js App Router was chosen for its file-system routing that mirrors the 13-page structure. Zustand avoids the boilerplate of React Context + reducers while providing selective re-renders. Radix UI provides WCAG-compliant primitives out of the box, eliminating the need to build accessible dialog, dropdown, and tooltip components from scratch. Tailwind CSS ensures design token consistency through CSS custom properties defined in `globals.css`.

## Component Tree

```
RootLayout (server)
└── ClientLayout (client)
    ├── LoadingScreen (initial load)
    └── MainLayout
        ├── Sidebar
        │   └── NavLink (×13 items)
        ├── Header
        │   ├── SearchInput → /search
        │   ├── NotificationBell (DropdownMenu)
        │   ├── ThemeToggle (DropdownMenu)
        │   └── UserAvatar (DropdownMenu)
        └── <main> (page content)
            ├── Dashboard (/)      → StatCard×4, MetricChart×2, etc.
            ├── Workspace          → ConversationList, ChatArea, InputBar
            ├── Projects           → Card grid, SearchInput, StatusFilter
            ├── Memory             → Tabs, Search, MemoryCard list
            ├── Knowledge          → Search, CollectionFilter, DocCard grid
            ├── Automation         → Tabs, AutomationCard list
            ├── Agents             → Tabs, AgentCard grid
            ├── Tools              → Search, CategoryFilter, ToolCard grid
            ├── Extensions         → Tabs, ExtensionCard list
            ├── Notifications      → Tabs, NotificationCard list
            ├── Search             → SearchInput, ResultCard list
            ├── Profile            → PersonalInfo, Preferences, Sessions
            └── Settings           → TabPanel (7 tabs), Switch×12, Select×8

Overlay:
└── CommandPalette (Cmd+K)
    ├── SearchInput
    └── CommandList (13 navigation items)
```

## State Management Approach

**Global State** (Zustand `app-store.ts`):

```typescript
interface AppState {
  theme: Theme;                    // "light" | "dark" | "system"
  sidebarCollapsed: boolean;
  notifications: Notification[];
  unreadCount: number;
  user: UserProfile | null;
  stats: DashboardStats | null;
  loading: boolean;
}
```

**Local State** (React `useState`):

All page-level data filtering, form inputs, and UI toggles use local state. Each page manages its own mock data and filter state internally, ensuring no leakage between routes.

**API State** (Custom `useApi<T>` hook):

```typescript
interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}
```

The `useApi` hook wraps any fetcher function with loading/error state. Convenience hooks (`useConversations`, `useProjects`, etc.) are pre-configured for each API endpoint.

### State Flow

```
User Action → Component (local state) → useApi hook → api.ts → Gateway
                                                                  ↓
Component (local state update) ← useApi state ← response
```

## API Integration Layer

**File**: `src/lib/api.ts`

- Base URL: `NEXT_PUBLIC_GATEWAY_URL` (default `http://localhost:8000`)
- All requests go through `/gateway` prefix
- Generic `fetchApi<T>(path, init)` function handles:
  - JSON headers
  - Error extraction from response body
  - `{ ok, data, error }` envelope unwrapping
- Organized by domain: `dashboard`, `conversations`, `projects`, `memory`, `knowledge`, `automations`, `agents`, `tools`, `extensions`, `notifications`, `search`, `profile`

**Architecture constraint**: The frontend contains NO business logic. All operations pass through the Gateway, which delegates to backend services.

## Page Routing Structure

| Route | Page Component | Description |
|---|---|---|
| `/` | `DashboardPage` | Ecosystem overview with stats, health, activity |
| `/workspace` | `WorkspacePage` | AI conversational workspace |
| `/projects` | `ProjectsPage` | Project management |
| `/memory` | `MemoryPage` | Memory center with archiving |
| `/knowledge` | `KnowledgePage` | Knowledge base with collections |
| `/automation` | `AutomationPage` | Workflows and scheduled tasks |
| `/agents` | `AgentsPage` | AI agent monitoring |
| `/tools` | `ToolsPage` | Tool registry |
| `/extensions` | `ExtensionsPage` | Extension management |
| `/notifications` | `NotificationsPage` | Notification center |
| `/search` | `SearchPage` | Cross-ecosystem search |
| `/profile` | `ProfilePage` | User profile and preferences |
| `/settings` | `SettingsPage` | Platform configuration (7 tabs) |

## Design System Tokens

Defined in `tailwind.config.ts` and `globals.css`:

- **Colors**: CSS custom properties in HSL format (27 color tokens)
- **Border Radius**: `--radius` with 3 levels (sm, md, lg)
- **Font Families**: `--font-sans` (Inter), `--font-mono` (JetBrains Mono)
- **Animations**: `fade-in`, `slide-in`, `pulse-subtle`, `scale-in`
- **Status Colors**: success, warning, error, info, pending
- **Sidebar Tokens**: background, foreground, muted, active

See [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) for complete token reference.

## Accessibility Approach

- All Radix UI primitives include built-in ARIA attributes
- Custom components use semantic HTML (`<nav>`, `<main>`, `<header>`, `<aside>`)
- Keyboard navigation: Command Palette uses Arrow keys + Enter
- Focus management: Command Palette auto-focuses input on open
- Color contrast: HSL tokens maintain WCAG 2.1 AA ratios in both themes
- Reduced motion: `prefers-reduced-motion` respected via framer-motion
- Screen reader: `aria-label` on icon buttons, `sr-only` utility classes

See [ACCESSIBILITY_GUIDE.md](./ACCESSIBILITY_GUIDE.md) for full details.
