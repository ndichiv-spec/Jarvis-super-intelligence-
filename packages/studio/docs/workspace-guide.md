# Workspace Guide

## Workspace Modules Overview

JARVIS Studio provides 16 workspace modules organized into 7 functional sections. Each module is a separate page under `src/app/studio/`.

| Module | Route | File | Purpose |
|---|---|---|---|
| Dashboard | `/studio` | `page.tsx` | Summary stats, health, quick nav |
| Workspace Manager | `/studio/workspace` | `workspace/page.tsx` | Organizations, projects, envs |
| Agent Designer | `/studio/agents` | `agents/page.tsx` | Agent catalog, capabilities, health |
| Workflow Designer | `/studio/workflows` | `workflows/page.tsx` | Definitions, executions, visual designer |
| Tool Manager | `/studio/tools` | `tools/page.tsx` | Tool registry, permissions, history |
| Extension Manager | `/studio/extensions` | `extensions/page.tsx` | Lifecycle, marketplace, updates |
| Knowledge Explorer | `/studio/knowledge` | `knowledge/page.tsx` | Collections, documents, search |
| Memory Inspector | `/studio/memory` | `memory/page.tsx` | Timeline, categories, policies, archive |
| Automation Monitor | `/studio/automation` | `automation/page.tsx` | Running workflows, history, performance |
| Event Monitor | `/studio/events` | `events/page.tsx` | Live stream, history, diagnostics |
| AI Runtime Manager | `/studio/ai` | `ai/page.tsx` | Providers, models, routing, usage |
| Security Center | `/studio/security` | `security/page.tsx` | Users, roles, policies, audit |
| Infrastructure Monitor | `/studio/infrastructure` | `infrastructure/page.tsx` | Component health, breakdowns |
| Observability Center | `/studio/observability` | `observability/page.tsx` | Metrics, logs, traces, alerts |
| API Explorer | `/studio/api-explorer` | `api-explorer/page.tsx` | Endpoint catalog, request builder, docs |
| Configuration Center | `/studio/config` | `config/page.tsx` | Feature flags, runtime config, profiles |
| Developer Console | `/studio/console` | `console/page.tsx` | Logs, diagnostics, validation, tasks, events |

## Dashboard

The landing page shows platform-wide summary statistics (active agents, running workflows, total tools, active extensions, platform uptime), a platform health overview grid (database, cache, vector store, message broker), active alerts, weekly activity chart, quick navigation links, and engineering summary cards. Data comes from `DashboardStats` via the `api.dashboard.stats()` endpoint.

## Workspace Manager

**Route:** `/studio/workspace`

Manages organizational hierarchy:
- **Workspace selector** — Dropdown to switch between workspaces (Main, Sandbox, Enterprise)
- **Overview tab** — StatCards for workspaces, organizations, projects, members; Organizations data table; Environment Metadata cards showing URL, version, and status for Dev/Staging/Production
- **Projects tab** — Data table with project name, status (StatusDot), progress bar, update time

State: `useState` for active tab + `Select` controlled component.

## Agent Designer

**Route:** `/studio/agents`

Design and monitor AI agents:
- **Catalog tab** — DataTable with agent name (icon), status (StatusDot), model (mono), capabilities (Badges), task count, uptime
- **Capabilities tab** — Card grid showing capability name, description, agent count, health status badge
- **Health tab** — Metric cards (active/idle/busy/error counts) + detailed agent status list with badges

## Workflow Designer

**Route:** `/studio/workflows`

Create and monitor automated workflows:
- **Definitions tab** — DataTable of workflow definitions (name, version badge, status, node count, updated)
- **Executions tab** — DataTable showing execution status, duration, trigger type (scheduled/manual/event)
- **Designer tab** — Placeholder for React Flow-based visual drag-and-drop workflow designer (using `@xyflow/react`)

StatCards: total workflows, published count, running executions, failed count.

## Tool Manager

**Route:** `/studio/tools`

Manage tool definitions and permissions:
- **Installed Tools tab** — DataTable with tool name (category icon), description, category badge, status, execution count, last used
- **Permissions tab** — Card grid showing each tool and its permission list with `CheckCircle2` indicators
- **Execution History tab** — DataTable of executions with success/failure icons, duration (mono), and timestamp

StatCards: total tools, active count, disabled count, total executions.

## Extension Manager

**Route:** `/studio/extensions`

Manage the extension lifecycle:
- **Installed tab** — DataTable with extension name/publisher, description, version, status badge (active/installed/disabled/error), permissions tags, install date
- **Available tab** — Extension Marketplace placeholder (EmptyState with "Browse Marketplace" action)
- **Updates tab** — DataTable showing installed → latest version diff with changelog and "Update" button per row

StatCards: total extensions, active, disabled, updates available.

Header action button: "Browse Extensions" with Download icon.

## Knowledge Explorer

**Route:** `/studio/knowledge`

Visualize and search knowledge collections:
- **Collections tab** — DataTable: collection name, description, type badge (vector/graph/hybrid), document count, relative update time
- **Documents tab** — DataTable: title, collection, type badge, tags, relationship count (GitBranch icon), update time
- **Search tab** — Search input with real-time filtering across title/tags/collection; results show title, collection, type badge, tags, relationship count

State: `useState` for searchQuery and activeTab. Uses `formatRelativeTime` utility.

## Memory Inspector

**Route:** `/studio/memory`

Transparent view into the agent memory platform:
- **Memory Timeline tab** — DataTable: content (truncated), type badge (fact/preference/context/relationship), source, confidence (progress bar + %), reasoning, relative time, active/archived status
- **Categories tab** — Card grid with category count and type badge
- **Policies tab** — DataTable: policy name, type badge, enabled Switch toggle, retention days
- **Archived tab** — DataTable with delete action buttons per row

## Automation Monitor

**Route:** `/studio/automation`

Real-time automation observability:
- **Running Workflows tab** — DataTable: name, started, duration, status with progress bar
- **History tab** — DataTable: workflow, status, started/completed times, duration, trigger badge
- **Performance tab** — Bar chart (MetricChart) for execution times + average duration card
- **Failures tab** — DataTable: workflow name, error message (truncated with destructive color), failed time, duration

StatCards: running, completed today, failed, avg duration.

## Event Monitor

**Route:** `/studio/events`

Live communication platform event stream:
- **Live Stream tab** — ScrollArea with event cards (type icon, severity badge, source, summary, correlationId, timestamp) and a pulsing "Live" indicator
- **History tab** — DataTable: type (icon), source, correlationId (mono with info color), severity badge, timestamp
- **Diagnostics tab** — Metric cards (total events, errors, warnings, info/debug), top event types with distribution bar, severity distribution grid

StatCards: events today, error rate, active correlations, avg processing time.

## AI Runtime Manager

**Route:** `/studio/ai`

Manage AI providers and model routing:
- **Providers tab** — DataTable: name, type, status (StatusDot), model count, avg latency (mono), total calls
- **Models tab** — DataTable: name (mono), provider, capabilities badges, status badge (active/experimental/deprecated), tokens in/out, cost
- **Routing tab** — Default configuration cards (default provider, fallback strategy, health check interval, circuit breaker) + per-model routing priority table
- **Usage tab** — Metric cards (total tokens in/out, estimated cost) + daily token usage bar chart

## Security Center

**Route:** `/studio/security`

User and role management:
- **Users tab** — DataTable: avatar initials, name, email, role badge (Admin/Engineer/Viewer), status (StatusDot), last active, MFA indicator (checkmark/x)
- **Roles tab** — DataTable: role name (Key icon), description, permission count, user count
- **Policies tab** — DataTable: policy name, description, rules count, enabled Switch (disabled)
- **Audit Log tab** — DataTable: actor, action badge (mono), resource, details, IP (mono), timestamp

## Infrastructure Monitor

**Route:** `/studio/infrastructure`

Display infrastructure health:
- **Component grid** — Cards showing each component: type icon, name, type badge, status badge, latency/uptime/last-checked metrics
- **Components tab** — DataTable: name (icon), type badge, status (StatusDot + badge), latency, uptime %, last checked
- **Health Summary tab** — StatCards (total, healthy, degraded, critical) + status breakdown list + component type breakdown cards with status dot indicators

## Observability Center

**Route:** `/studio/observability`

Unified observability:
- **Metrics tab** — Dual bar charts (API calls over time, error rate) + metric cards (avg response time, total requests, error count, uptime)
- **Logs tab** — DataTable: level badge (debug/info/warn/error), source (mono), message, timestamp
- **Traces tab** — Expandable trace table: name (mono), duration, status badge, span count, timestamp; expanded rows show span-level details
- **Alerts tab** — DataTable: title with severity icon, severity badge, source (mono), message, timestamp, ack status

## API Explorer

**Route:** `/studio/api-explorer`

Interactive gateway API browser:
- **Request Builder card** — Method select (GET/POST/PUT/PATCH/DELETE with color coding), path input, Send button
- **Endpoints tab** — DataTable: method badge (color-coded), path (mono), description, version badge
- **Documentation tab** — Detailed view with method/path header, description, parameters table (name/type/required/description), example request/response side-by-side

StatCards: total endpoints, GET count, POST count, other methods count.

## Configuration Center

**Route:** `/studio/config`

Platform configuration management:
- **Feature Flags tab** — DataTable: key (mono), name, description, enabled Switch (disabled), environment badge, update time
- **Runtime Configuration tab** — DataTable: key (mono), value (mono, truncated), type badge, description, update time, Edit action button
- **Profiles tab** — DataTable: name (FileJson icon), description, config key count, Active/Inactive status badge

StatCards: total flags, enabled count, runtime configs, active profiles.

## Developer Console

**Route:** `/studio/console`

Integrated engineering console:
- **Logs tab** — Terminal-styled log output in a dark theme ScrollArea (`#0d1117` background): level icon + level badge + message + source + timestamp
- **Diagnostics tab** — Card grid: CPU load, memory, network latency, database pool, message queue, disk I/O with status badges
- **Validation tab** — DataTable: rule (mono), status badge (pass/fail/warn), scope, message
- **Tasks tab** — DataTable: task name, status icon + text (success/running/failed/pending), duration, started
- **Events tab** — DataTable: type, source, severity badge, summary, timestamp
- **Command bar** — Input + Execute button at the bottom

## Common Patterns

Every workspace page follows this structure:

1. `PageHeader` — Title, description, optional action buttons in `actions` prop
2. `motion.div` with `containerVariants` / `itemVariants` — Staggered fade-in animations
3. StatCards grid (3-5 cards) — Top-level metrics
4. `Tabs` component — Sub-navigation for different data views
5. `Card` + `DataTable` or custom content — Primary data display
6. `CardContent className="p-0"` — For DataTable with flush edges
