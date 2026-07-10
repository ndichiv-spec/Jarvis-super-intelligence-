# JARVIS Home — Navigation Guide

## Sidebar Navigation

The sidebar (`src/components/layout/sidebar.tsx`) serves as the primary navigation rail.

### Structure

**Primary Nav** (top section):
| Icon | Label | Route |
|---|---|---|
| `LayoutDashboard` | Home | `/` |
| `MessageSquare` | AI Workspace | `/workspace` |
| `FolderKanban` | Projects | `/projects` |
| `Brain` | Memory Center | `/memory` |
| `BookOpen` | Knowledge Center | `/knowledge` |
| `Zap` | Automation | `/automation` |
| `Bot` | Agents | `/agents` |
| `Wrench` | Tools | `/tools` |
| `Puzzle` | Extensions | `/extensions` |

**Secondary Nav** (bottom section, separated by border):
| Icon | Label | Route |
|---|---|---|
| `Bell` | Notifications | `/notifications` |
| `Search` | Search | `/search` |
| `User` | Profile | `/profile` |
| `Settings` | Settings | `/settings` |

### Behavior

- **Active state**: Determined by `usePathname()` — exact match for `/`, prefix match for all other routes
- **Collapsed mode**: Toggle button at bottom, reduces width from 240px to 64px
- **Tooltips**: Shown on hover when collapsed, hidden when expanded
- **Animation**: Label text fades in/out using framer-motion `AnimatePresence`
- **Badge**: Unread notification count shown on the Notifications nav item
- **Responsive**: Collapse toggle is hidden on mobile (`hidden lg:flex`)

## Header Navigation

The header (`src/components/layout/header.tsx`) provides secondary navigation:

| Element | Action |
|---|---|
| Search input | Focus navigates to `/search` |
| Notification bell | Opens notification dropdown, shows unread badge |
| Theme toggle (Sun/Moon) | Cycles through light, dark, system |
| User avatar | Dropdown with Profile and Settings links |

### Search Bar

- Visible on `sm:` breakpoint and above
- Wrapped in a `<Link href="/search">` for full-click navigation
- Placeholder: "Search anything..."

## Command Palette (Cmd+K)

The Command Palette (`src/components/shared/command-palette.tsx`) provides keyboard-driven navigation.

### Trigger

- **Global shortcut**: `Cmd+K` (macOS) / `Ctrl+K` (Windows/Linux)
- **Escape**: Closes the palette

### Interface

- Modal overlay with backdrop blur
- Centered dialog with search input
- 13 navigation items with icons, descriptions, and category labels
- Real-time filtering as user types
- Keyboard navigation: Arrow Up/Down to select, Enter to navigate

### Items

All 13 sidebar routes are registered as command items, each with:
- `id`: route identifier
- `label`: human-readable name
- `description`: short context
- `icon`: Lucide icon component
- `href`: target route
- `category`: currently "Navigation" for all items

## Breadcrumb System

JARVIS Home does not currently implement breadcrumbs. The `PageHeader` component provides the current page title and description, acting as a lightweight replacement. Breadcrumbs can be added by composing a breadcrumb trail from the current path segments.

## Keyboard Shortcuts

| Shortcut | Action | Implementation |
|---|---|---|
| `Cmd+K` / `Ctrl+K` | Toggle Command Palette | `useKeyboardShortcut` in `command-palette.tsx` |
| `Escape` | Close Command Palette | `useKeyboardShortcut` in `command-palette.tsx` |
| `Arrow Up/Down` | Navigate command list | `onKeyDown` handler |
| `Enter` | Execute selected command | `onKeyDown` handler |
| `Tab` | Focus traversal (default) | Native browser behavior |

### Keyboard Hook

The `useKeyboardShortcut` (`src/hooks/use-keyboard.ts`) hook supports:
- `meta` (Cmd on Mac, Windows key on PC)
- `ctrl`
- `shift`
- `alt`
- `key` (case-insensitive matching)

Usage:
```typescript
useKeyboardShortcut([
  { key: "k", meta: true, handler: () => toggle() },
  { key: "Escape", handler: () => close() },
]);
```

## Responsive Behavior

| Breakpoint | Sidebar | Header | Pages |
|---|---|---|---|
| **Desktop** (lg+) | Expanded (240px) w/ collapse toggle | Full search bar, all controls | Multi-column grids |
| **Tablet** (md) | Collapsible states | Condensed search | 2-column grids |
| **Mobile** (< md) | Sidebar hidden (workspace: ConversationList hidden) | Search icon + modal | Single-column, stacked |

### Workspace Page Specific

- `< md`: `ConversationList` sidebar is hidden (`hidden md:flex`)
- Chat messages stack vertically with avatar alignment

### Dashboard Page

- StatCards: 1 col → 2 col (sm) → 4 col (lg)
- System Health: 1 col → 2 col on large
- MetricCharts: side-by-side on lg

### All List Pages

- Grid layouts use responsive cols: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- Search/filter bars stack vertically on small screens
