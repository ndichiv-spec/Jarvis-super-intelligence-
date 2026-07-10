# Component Catalog

## UI Primitives

Located in `src/components/ui/`. Built on Radix UI primitives with class-variance-authority.

### Button

```tsx
import { Button } from "@/components/ui/button";
```

| Prop | Type | Default | Description |
|---|---|---|---|
| variant | `"default" \| "destructive" \| "outline" \| "secondary" \| "ghost" \| "link"` | `"default"` | Visual style |
| size | `"default" \| "sm" \| "lg" \| "icon"` | `"default"` | Size preset |
| asChild | `boolean` | `false` | Render as child (Slot) |
| className | `string` | — | Additional classes |

**Examples:**
```tsx
<Button>Default</Button>
<Button variant="destructive" size="sm">Delete</Button>
<Button variant="ghost" size="icon"><Trash2 className="h-4 w-4" /></Button>
<Button asChild><Link href="/studio">Link Button</Link></Button>
```

### Card

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
```

| Component | Props |
|---|---|
| `Card` | `className`, `children` |
| `CardHeader` | `className`, `children` |
| `CardTitle` | `className`, `children` |
| `CardDescription` | `className`, `children` |
| `CardContent` | `className`, `children` |
| `CardFooter` | `className`, `children` |

**Example:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description text</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer actions</CardFooter>
</Card>
```

### Badge

```tsx
import { Badge } from "@/components/ui/badge";
```

| Prop | Type | Default |
|---|---|---|
| variant | `"default" \| "secondary" \| "destructive" \| "outline" \| "success" \| "warning" \| "info"` | `"default"` |

**Example:**
```tsx
<Badge variant="success">Active</Badge>
<Badge variant="warning">Degraded</Badge>
<Badge variant="info">v2.0</Badge>
```

### Tabs

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
```

| Component | Props |
|---|---|
| `Tabs` | `value`, `onValueChange`, `defaultValue` (from Radix) |
| `TabsList` | `className`, `children` |
| `TabsTrigger` | `value`, `className`, `children` |
| `TabsContent` | `value`, `className`, `children` |

**Example:**
```tsx
<Tabs defaultValue="catalog">
  <TabsList>
    <TabsTrigger value="catalog">Catalog</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  <TabsContent value="catalog">...</TabsContent>
  <TabsContent value="settings">...</TabsContent>
</Tabs>
```

### Dialog

```tsx
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "@/components/ui/dialog";
```

**Features:** Radix modal with overlay, scale-in animation, X close button.

### DropdownMenu

```tsx
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
```

**Features:** Portal-based menu with scale-in animation, inset items support.

### Select

```tsx
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
```

**Features:** Radix select with chevron icon, portal content, popper positioning.

### Switch

```tsx
import { Switch } from "@/components/ui/switch";
```

| Prop | Type | Note |
|---|---|---|
| All Radix Switch props | — | `checked`, `onCheckedChange`, `disabled` |

### Input

```tsx
import { Input } from "@/components/ui/input";
```

| Prop | Type |
|---|---|
| Standard HTML input attributes | `type`, `placeholder`, `className`, etc. |

### Progress

```tsx
import { Progress } from "@/components/ui/progress";
```

| Prop | Type |
|---|---|
| `value` | `number` (0-100) |

### Separator

```tsx
import { Separator } from "@/components/ui/separator";
```

| Prop | Type | Default |
|---|---|---|
| `orientation` | `"horizontal" \| "vertical"` | `"horizontal"` |

### Tooltip

```tsx
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
```

| Prop | Type | Default |
|---|---|---|
| `sideOffset` | `number` | `4` |

### Avatar

```tsx
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
```

### ScrollArea

```tsx
import { ScrollArea } from "@/components/ui/scroll-area";
```

## Shared Components

Located in `src/components/shared/`. Used across all workspace pages.

### PageHeader

```tsx
import { PageHeader } from "@/components/shared/page-header";
```

| Prop | Type | Required |
|---|---|---|
| `title` | `string` | Yes |
| `description` | `string` | No |
| `actions` | `React.ReactNode` | No |
| `className` | `string` | No |

**Example:**
```tsx
<PageHeader
  title="Agent Designer"
  description="Design, configure, and monitor your AI agents"
  actions={<Button size="sm">Create Agent</Button>}
/>
```

### StatCard

```tsx
import { StatCard } from "@/components/shared/stat-card";
```

| Prop | Type | Required |
|---|---|---|
| `title` | `string` | Yes |
| `value` | `string \| number` | Yes |
| `icon` | `LucideIcon` | Yes |
| `description` | `string` | No |
| `trend` | `{ value: number; positive: boolean }` | No |
| `className` | `string` | No |

**Example:**
```tsx
<StatCard
  title="Active Agents"
  value={8}
  icon={Bot}
  description="3 running tasks"
  trend={{ value: 12, positive: true }}
/>
```

### DataTable

```tsx
import { DataTable, type Column } from "@/components/shared/data-table";
```

| Prop | Type | Required |
|---|---|---|
| `columns` | `Column<T>[]` | Yes |
| `data` | `T[]` (must have `id: string`) | Yes |
| `onRowClick` | `(item: T) => void` | No |
| `className` | `string` | No |
| `emptyMessage` | `string` | No |

**Column interface:**
```ts
interface Column<T> {
  key: string;
  header: string;
  cell: (item: T) => React.ReactNode;
  className?: string;
  sortable?: boolean;
}
```

**Example:**
```tsx
const columns: Column<Agent>[] = [
  { key: "name", header: "Name", cell: (a) => <span className="font-medium">{a.name}</span> },
  { key: "status", header: "Status",
    cell: (a) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={a.status} />
        <span className="text-xs capitalize">{a.status}</span>
      </div>
    ),
  },
  { key: "tasks", header: "Tasks", className: "text-right",
    cell: (a) => <span className="tabular-nums">{a.taskCount}</span>,
  },
];

<DataTable columns={columns} data={agents} emptyMessage="No agents found" onRowClick={(agent) => console.log(agent)} />
```

### StatusDot

```tsx
import { StatusDot } from "@/components/shared/status-dot";
```

| Prop | Type | Required |
|---|---|---|
| `status` | `StatusType` | Yes |
| `className` | `string` | No |

Supported status values and their colors:

| Status | Color |
|---|---|
| `healthy`, `active`, `success`, `available`, `running` | `bg-status-success` (green) |
| `degraded`, `warning`, `busy`, `maintenance` | `bg-status-warning` (amber) |
| `pending`, `idle`, `draft` | `bg-status-pending` (gray) |
| `critical`, `error`, `suspended` | `bg-status-error` (red) |
| `inactive`, `disabled`, `archived` | `bg-muted-foreground` |

**Example:**
```tsx
<StatusDot status="healthy" />
<StatusDot status="critical" className="h-3 w-3" />
```

### MetricChart

```tsx
import { MetricChart } from "@/components/shared/metric-chart";
```

| Prop | Type | Required | Default |
|---|---|---|---|
| `title` | `string` | Yes | — |
| `data` | `{ label: string; value: number }[]` | Yes | — |
| `color` | `string` | No | `"hsl(var(--primary))"` |

**Example:**
```tsx
<MetricChart
  title="Weekly Activity"
  data={[
    { label: "Mon", value: 24 },
    { label: "Tue", value: 18 },
  ]}
/>
```

### EmptyState

```tsx
import { EmptyState } from "@/components/shared/empty-state";
```

| Prop | Type | Required | Default |
|---|---|---|---|
| `icon` | `React.ElementType` | No | `Inbox` |
| `title` | `string` | Yes | — |
| `description` | `string` | No | — |
| `action` | `React.ReactNode` | No | — |
| `className` | `string` | No | — |

**Example:**
```tsx
<EmptyState
  icon={Search}
  title="No results found"
  description="Try a different search term"
  action={<Button>Clear Filters</Button>}
/>
```

### SectionHeader

```tsx
import { SectionHeader } from "@/components/shared/section-header";
```

| Prop | Type | Required |
|---|---|---|
| `title` | `string` | Yes |
| `description` | `string` | No |
| `action` | `{ label: string; href: string }` | No |
| `className` | `string` | No |

**Example:**
```tsx
<SectionHeader
  title="Active Incidents"
  description="Current platform issues"
  action={{ label: "View All", href: "/studio/observability" }}
/>
```

### LoadingScreen

```tsx
import { LoadingScreen } from "@/components/shared/loading-screen";
```

Full-screen centered loading state with "JS" logo and pulsing animation. Used in `client-layout.tsx` during initial data load.

## Layout Components

Located in `src/components/layout/`.

### Sidebar

```tsx
import { Sidebar } from "@/components/layout/sidebar";
```

- Reads `sidebarCollapsed` and `toggleSidebar` from `useAppStore`
- No props — self-contained
- Renders 7 sections with 17 nav items
- Collapsible with tooltip support

### Header

```tsx
import { Header } from "@/components/layout/header";
```

- Displays current workspace name + environment badge
- Global search input (placeholder)
- Theme toggle dropdown (Light / Dark / System)
- User menu dropdown (avatar, name, email, role, settings, sign out)

### MainLayout

```tsx
import { MainLayout } from "@/components/layout/main-layout";
```

| Prop | Type |
|---|---|
| `children` | `React.ReactNode` |

- Sidebar + Header + `<main>` wrapper
- Hydrates mock user, workspace, and organization data on mount
- Uses `flex h-screen` for full-height layout

## Composition Patterns

```tsx
// Standard page composition
<>
  <PageHeader title="..." description="..." />
  <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
    <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard ... />
      <StatCard ... />
    </motion.div>
    <motion.div variants={itemVariants}>
      <Card>
        <CardContent className="p-0">
          <Tabs defaultValue="tab1">
            <TabsList>...</TabsList>
            <TabsContent value="tab1">
              <DataTable ... />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </motion.div>
  </motion.div>
</>
```
