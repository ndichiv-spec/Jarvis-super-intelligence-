# JARVIS Home — Component Catalog

## Shared Components

All shared components live in `src/components/shared/`. They are stateless (or accept state as props) and domain-agnostic.

---

### StatCard

A metric display card with icon, value, label, optional trend indicator, and optional description.

**File**: `src/components/shared/stat-card.tsx`

```typescript
interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: { value: number; positive: boolean };
  className?: string;
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `title` | `string` | Yes | Label displayed above the value |
| `value` | `string \| number` | Yes | Primary metric value |
| `icon` | `LucideIcon` | Yes | Icon rendered in a tinted circle |
| `description` | `string` | No | Supplementary text below value |
| `trend` | `{ value: number, positive: boolean }` | No | Percentage change with directional color |
| `className` | `string` | No | Additional CSS classes |

**Usage**:
```tsx
<StatCard
  title="Active Projects"
  value={12}
  icon={FolderKanban}
  trend={{ value: 8, positive: true }}
/>
```

---

### PageHeader

Standardized page title bar with description and optional action slot.

**File**: `src/components/shared/page-header.tsx`

```typescript
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `title` | `string` | Yes | Page title (`<h1>`) |
| `description` | `string` | No | Subtitle in muted text |
| `actions` | `React.ReactNode` | No | Action buttons rendered on the right |
| `className` | `string` | No | Additional CSS classes |

**Usage**:
```tsx
<PageHeader
  title="Projects"
  description="Manage your projects and track progress"
  actions={<Button><Plus className="mr-2 h-4 w-4" />New Project</Button>}
/>
```

---

### StatusDot

A small colored indicator dot for status visualization.

**File**: `src/components/shared/status-dot.tsx`

```typescript
interface StatusDotProps {
  status: "healthy" | "degraded" | "critical" | "active" | "inactive"
        | "error" | "warning" | "success" | "pending" | "running"
        | "idle" | "busy";
  className?: string;
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `status` | `string` (union) | Yes | Status value mapped to a color |
| `className` | `string` | No | Additional CSS classes |

**Color Map**:
| Status | Color |
|---|---|
| `healthy`, `active`, `success` | `bg-status-success` (green) |
| `running` | `bg-status-info` (blue) |
| `degraded`, `warning`, `busy` | `bg-status-warning` (amber) |
| `pending`, `idle` | `bg-status-pending` (gray) |
| `critical`, `error` | `bg-status-error` (red) |
| `inactive` | `bg-muted-foreground` |

**Usage**:
```tsx
<StatusDot status="healthy" />
<StatusDot status="error" className="mr-1" />
```

---

### EmptyState

Centered empty/placeholder state with icon, title, description, and optional action.

**File**: `src/components/shared/empty-state.tsx`

```typescript
interface EmptyStateProps {
  icon?: React.ElementType;    // default: Inbox
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}
```

**Usage**:
```tsx
<EmptyState
  icon={FolderKanban}
  title="No projects found"
  description="Create your first project to get started"
  action={<Button><Plus className="mr-2 h-4 w-4" />New Project</Button>}
/>
```

---

### LoadingScreen

Full-screen loading state shown during initial app hydration.

**File**: `src/components/shared/loading-screen.tsx`

```typescript
// No props
```

**Display**: Centered "J" logo, animated progress bar, "Loading JARVIS Home..." text.

---

### ErrorState

Error display with optional retry button.

**File**: `src/components/shared/error-state.tsx`

```typescript
interface ErrorStateProps {
  title?: string;          // default: "Something went wrong"
  message?: string;        // default: "An error occurred while loading this content."
  onRetry?: () => void;
  className?: string;
}
```

**Usage**:
```tsx
<ErrorState
  title="Failed to load agents"
  message="Check your connection and try again."
  onRetry={() => fetchAgents()}
/>
```

---

### MetricChart

A simple bar chart component for displaying metric data over labels.

**File**: `src/components/shared/metric-chart.tsx`

```typescript
interface DataPoint {
  label: string;
  value: number;
}

interface MetricChartProps {
  title: string;
  data: DataPoint[];
  className?: string;
  height?: number;         // default: 120
  color?: string;          // default: "hsl(var(--primary))"
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `title` | `string` | Yes | Chart card title |
| `data` | `DataPoint[]` | Yes | Array of `{ label, value }` |
| `height` | `number` | No | Chart area height in px (default: 120) |
| `color` | `string` | No | Bar fill color (default: primary) |
| `className` | `string` | No | Additional CSS classes |

**Usage**:
```tsx
<MetricChart
  title="Weekly Activity"
  data={[
    { label: "Mon", value: 24 },
    { label: "Tue", value: 18 },
    // ...
  ]}
/>

<MetricChart
  title="API Calls"
  data={usageData}
  color="hsl(var(--status-info))"
/>
```

---

### SectionHeader

Section heading with optional description and action link.

**File**: `src/components/shared/section-header.tsx`

```typescript
interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: { label: string; href: string };
  className?: string;
}
```

**Usage**:
```tsx
<SectionHeader
  title="Platform Summary"
  description="Key metrics at a glance"
  action={{ label: "View Details", href: "/settings" }}
/>
```

---

### DataTable

Generic table component with typed columns, sortable headers, and row click support.

**File**: `src/components/shared/data-table.tsx`

```typescript
interface Column<T> {
  key: string;
  header: string;
  cell: (item: T) => React.ReactNode;
  className?: string;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  className?: string;
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `columns` | `Column<T>[]` | Yes | Column definitions with header and cell renderer |
| `data` | `T[]` | Yes | Data array (items must have `id: string`) |
| `onRowClick` | `(item: T) => void` | No | Row click callback, adds cursor pointer |
| `className` | `string` | No | Additional CSS classes |

**Usage**:
```tsx
<DataTable
  columns={[
    { key: "name", header: "Name", cell: (item) => item.name },
    { key: "status", header: "Status", cell: (item) => <StatusDot status={item.status} /> },
  ]}
  data={items}
  onRowClick={(item) => router.push(`/projects/${item.id}`)}
/>
```

---

### CommandPalette

Keyboard-driven navigation overlay triggered by `Cmd+K`.

**File**: `src/components/shared/command-palette.tsx`

```typescript
// No props — self-contained with internal state
```

**Internal State**: `open`, `query`, `selectedIndex`

**Commands**: 13 navigation items registered statically, each with `{ id, label, description, icon, href, category }`.

**Behavior**: Filter-as-you-type, keyboard navigation (Arrow Up/Down), Enter to navigate, Escape/backdrop to close.

**Usage**: Rendered once in `MainLayout` (or `ClientLayout`):
```tsx
<CommandPalette />
```

---

### ConversationList

Sidebar for the AI Workspace showing conversation history with search, creation, and deletion.

**File**: `src/components/workspace/conversation-list.tsx`

```typescript
interface Conversation {
  id: string;
  title: string;
  preview: string;
  date: Date;
}

interface ConversationListProps {
  conversations: Conversation[];
  activeId?: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete?: (id: string) => void;
}
```

**Props**:
| Prop | Type | Required | Description |
|---|---|---|---|
| `conversations` | `Conversation[]` | Yes | List of conversations |
| `activeId` | `string` | No | Currently selected conversation ID |
| `onSelect` | `(id: string) => void` | Yes | Selection callback |
| `onNew` | `() => void` | Yes | New conversation callback |
| `onDelete` | `(id: string) => void` | No | Delete callback, shows trash icon on hover |

**Usage**:
```tsx
<ConversationList
  conversations={conversations}
  activeId={activeConv}
  onSelect={handleSelectConversation}
  onNew={handleNewConversation}
  onDelete={handleDeleteConversation}
/>
```

---

## UI Primitives (Radix-based)

Located in `src/components/ui/`, these are thin wrappers around Radix UI primitives styled with the design system:

| Component | Radix Primitive | Key Features |
|---|---|---|
| `Button` | — | Variants: default, outline, ghost, destructive. Sizes: sm, default, lg, icon |
| `Card` | — | Card, CardHeader, CardTitle, CardDescription, CardContent |
| `Badge` | — | Variants: default, outline, secondary |
| `Input` | — | Styled text input with focus ring |
| `Avatar` | `@radix-ui/react-avatar` | Avatar root, image, fallback |
| `Dialog` | `@radix-ui/react-dialog` | Modal dialog with overlay |
| `DropdownMenu` | `@radix-ui/react-dropdown-menu` | Menu with items, separators, labels |
| `Tabs` | `@radix-ui/react-tabs` | Tab list, triggers, content panels |
| `Tooltip` | `@radix-ui/react-tooltip` | Tooltip provider, trigger, content |
| `Select` | `@radix-ui/react-select` | Native-feel select with portal |
| `Switch` | `@radix-ui/react-switch` | Toggle switch |
| `Slider` | `@radix-ui/react-slider` | Range slider |
| `Progress` | `@radix-ui/react-progress` | Progress bar |
| `ScrollArea` | `@radix-ui/react-scroll-area` | Custom scrollbar |
| `Separator` | `@radix-ui/react-separator` | Horizontal/vertical divider |
