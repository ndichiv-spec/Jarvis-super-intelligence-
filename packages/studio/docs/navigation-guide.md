# Navigation Guide

## Sidebar Structure

The sidebar (`src/components/layout/sidebar.tsx`) defines seven nav sections with 17 items. Sections are rendered as uppercase section headers with indented nav links.

```
┌──────────────────────────────┐
│  [JS] JARVIS Studio          │
├──────────────────────────────┤
│  OVERVIEW                    │
│    ◉ Dashboard               │
│                              │
│  DESIGN                      │
│    ◉ Workspace Manager       │
│    ◉ Agent Designer          │
│    ◉ Workflow Designer       │
│    ◉ Tool Manager            │
│    ◉ Extension Manager       │
│                              │
│  KNOWLEDGE                   │
│    ◉ Knowledge Explorer      │
│    ◉ Memory Inspector        │
│                              │
│  OBSERVE                     │
│    ◉ Automation Monitor      │
│    ◉ Event Monitor           │
│                              │
│  MANAGE                      │
│    ◉ AI Runtime Manager      │
│    ◉ Security Center         │
│    ◉ Infrastructure Monitor  │
│                              │
│  ANALYZE                     │
│    ◉ Observability Center    │
│                              │
│  DEVELOP                     │
│    ◉ API Explorer            │
│    ◉ Configuration Center    │
│    ◉ Developer Console       │
│                              │
│  ◀ Collapse                  │
└──────────────────────────────┘
```

## Section and Item Reference

| Section | Label | href | Icon | Description |
|---|---|---|---|---|
| Overview | Dashboard | `/studio` | LayoutDashboard | Summary stats, platform health, active alerts, quick navigation |
| Design | Workspace Manager | `/studio/workspace` | SquareDashed | Organizations, projects, environments |
| Design | Agent Designer | `/studio/agents` | Bot | Agent catalog, capabilities matrix, health status |
| Design | Workflow Designer | `/studio/workflows` | GitBranch | Workflow definitions, executions, visual designer |
| Design | Tool Manager | `/studio/tools` | Wrench | Tool registry, permissions, execution history |
| Design | Extension Manager | `/studio/extensions` | Puzzle | Extension lifecycle, marketplace, updates |
| Knowledge | Knowledge Explorer | `/studio/knowledge` | BookOpen | Collections, documents, graph relationships, semantic search |
| Knowledge | Memory Inspector | `/studio/memory` | Brain | Memory timeline, categories, policies, archival |
| Observe | Automation Monitor | `/studio/automation` | PlayCircle | Running workflows, history, performance, failures |
| Observe | Event Monitor | `/studio/events` | Radio | Live event stream, history, diagnostics, severity distribution |
| Manage | AI Runtime Manager | `/studio/ai` | Cpu | Provider management, model catalog, routing, token usage |
| Manage | Security Center | `/studio/security` | Shield | Users, roles, security policies, audit log |
| Manage | Infrastructure Monitor | `/studio/infrastructure` | Server | Component health grid, status breakdown, type breakdown |
| Analyze | Observability Center | `/studio/observability` | BarChart3 | Metrics, logs, distributed traces, alerts |
| Develop | API Explorer | `/studio/api-explorer` | BookType | Interactive request builder, endpoint catalog, docs |
| Develop | Configuration Center | `/studio/config` | Settings | Feature flags, runtime config, config profiles |
| Develop | Developer Console | `/studio/console` | Terminal | Console output, diagnostics, validation, tasks, events |

## Navigation Implementation

- Active state is determined by `usePathname()`: exact match for Dashboard, `startsWith` for all others
- Collapsed mode (w-14 vs w-56) animates labels via Framer Motion `AnimatePresence`
- Tooltips appear on the right when collapsed (`TooltipContent side="right"`)
- Sidebar toggle button at the bottom (visible on `lg` breakpoint)
- Scrollbar-thin overflow styling for long nav lists

## Workspace Navigation Patterns

- **Header breadcrumb**: The header shows the current workspace name and environment badge
- **Tab-based sub-navigation**: Every workspace page uses `<Tabs>` for sub-sections (e.g., Catalog / Capabilities / Health)
- **Quick Navigation card**: The Dashboard includes a 10-item quick-nav card as an alternative to sidebar navigation
- **StatCards always on top**: Every page renders 3-5 StatCards at the top for key metrics before tab content

## Keyboard Shortcuts (Concept)

The Studio architecture supports keyboard shortcuts; the following are reserved for future implementation:

| Shortcut | Action |
|---|---|
| `Cmd/Ctrl + K` | Search palette |
| `Cmd/Ctrl + B` | Toggle sidebar |
| `Cmd/Ctrl + ,` | Settings |
| `Cmd/Ctrl + 1-7` | Navigate to section (by order) |
| `Escape` | Close panel / clear selection |
| `?` | Show keyboard shortcuts help |
