# JARVIS Home — Design System

## Color Tokens

Colors are defined as HSL CSS custom properties in `globals.css` and consumed via Tailwind's `hsl(var(--token))` pattern.

### Light Theme (`:root`)

| Token | HSL Value | Description |
|---|---|---|
| `--background` | `220 20% 98%` | App background |
| `--foreground` | `220 20% 12%` | Primary text |
| `--card` | `0 0% 100%` | Card surface |
| `--card-foreground` | `220 20% 12%` | Card text |
| `--popover` | `0 0% 100%` | Popover/dropdown surface |
| `--popover-foreground` | `220 20% 12%` | Popover text |
| `--primary` | `220 70% 50%` | Primary accent (blue) |
| `--primary-foreground` | `0 0% 100%` | Text on primary |
| `--secondary` | `220 15% 94%` | Secondary surface |
| `--secondary-foreground` | `220 20% 20%` | Secondary text |
| `--muted` | `220 15% 94%` | Muted background |
| `--muted-foreground` | `220 10% 50%` | Muted text |
| `--accent` | `220 15% 90%` | Hover/active surface |
| `--accent-foreground` | `220 20% 20%` | Accent text |
| `--destructive` | `0 84% 60%` | Destructive/error |
| `--destructive-foreground` | `0 0% 100%` | Text on destructive |
| `--border` | `220 15% 88%` | Borders and dividers |
| `--input` | `220 15% 88%` | Input borders |
| `--ring` | `220 70% 50%` | Focus ring |
| `--radius` | `0.5rem` | Border radius |

### Sidebar Tokens (Light)

| Token | HSL Value |
|---|---|
| `--sidebar` | `220 25% 97%` |
| `--sidebar-foreground` | `220 20% 20%` |
| `--sidebar-muted` | `220 10% 50%` |
| `--sidebar-active` | `220 70% 50%` |

### Status Tokens

| Token | HSL Value (Light/Dark) | Usage |
|---|---|---|
| `--status-success` | `142 70% 45%` | Healthy, active, success states |
| `--status-warning` | `38 92% 50%` | Warning, busy, degraded states |
| `--status-error` | `0 84% 60%` / `0 70% 50%` | Error, critical states |
| `--status-info` | `200 90% 50%` | Info, running states |
| `--status-pending` | `220 10% 55%` / `220 10% 50%` | Idle, pending states |

### Dark Theme (`.dark`)

All light theme tokens have dark counterparts, characterized by:
- Lower luminance backgrounds (e.g., `220 25% 8%` for background)
- Higher luminance foregrounds (e.g., `220 10% 92%` for text)
- Slightly brighter primary accent (`220 70% 55%` vs `50%`)
- Deeper borders (`220 20% 20%` vs `88%`)

## Typography

### Font Families

```css
--font-sans: "Inter", system-ui, -apple-system, sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", monospace;
```

- **Inter**: Primary sans-serif font for UI text, loaded via `next/font/google` with `display: swap`
- **JetBrains Mono**: Monospace font for code blocks and technical content
- **System fallback**: `system-ui, sans-serif` and `monospace` respectively

### Type Scale

| Element | Size | Weight | Tracking |
|---|---|---|---|
| Page title (`h1`) | `text-2xl` | `font-semibold` | `tracking-tight` |
| Section title (`h2`) | `text-lg` | `font-semibold` | — |
| Card title | `text-base` | `font-semibold` | — |
| Body text | `text-sm` | `font-normal` | — |
| Description | `text-xs` | — | — |
| Stat value | `text-2xl` | `font-semibold` | — |
| Small label | `text-[10px]` | `font-medium` | — |

### Font Features

```css
body {
  font-feature-settings: "rlig" 1, "calt" 1;
}
```

`rlig` (contextual ligatures) and `calt` (contextual alternates) are enabled for improved readability.

## Spacing & Sizing

JARVIS Home uses Tailwind's default spacing scale. Key patterns:

| Pattern | Value | Usage |
|---|---|---|
| Page padding | `px-6 py-4` | Content horizontal padding |
| Section gap | `space-y-6` | Between major sections |
| Card grid gap | `gap-4` | Between grid items |
| Stack spacing | `space-y-4` | Card content stacks |
| Inline gap | `gap-2`, `gap-3` | Button groups, inline elements |

### Layout Constants

| Element | Width/Height |
|---|---|
| Sidebar (expanded) | `w-60` (240px) |
| Sidebar (collapsed) | `w-16` (64px) |
| Header | `h-14` (56px) |
| ConversationList sidebar | `w-64` (256px) |
| Max content width | `max-w-3xl` (768px) — workspace chat |
| Max search width | `max-w-2xl` (672px) — search page |

## Animation System

### Tailwind Keyframes (`tailwind.config.ts`)

```typescript
keyframes: {
  "fade-in": {
    "0%": { opacity: "0", transform: "translateY(4px)" },
    "100%": { opacity: "1", transform: "translateY(0)" },
  },
  "slide-in": {
    "0%": { opacity: "0", transform: "translateX(-8px)" },
    "100%": { opacity: "1", transform: "translateX(0)" },
  },
  "pulse-subtle": {
    "0%, 100%": { opacity: "1" },
    "50%": { opacity: "0.7" },
  },
  "scale-in": {
    "0%": { transform: "scale(0.95)", opacity: "0" },
    "100%": { transform: "scale(1)", opacity: "1" },
  },
}
```

### Animation Classes

| Class | Timing | Usage |
|---|---|---|
| `animate-fade-in` | `0.3s ease-out` | Page content entrance |
| `animate-slide-in` | `0.2s ease-out` | Sidebar items, list entries |
| `animate-pulse-subtle` | `2s ease-in-out infinite` | Active indicators, loading |
| `animate-scale-in` | `0.2s ease-out` | Dialogs, command palette |

### Framer Motion

Used for component-level animation:

- **Dashboard**: `containerVariants` with `staggerChildren: 0.05` for staggered grid entrance
- **Command Palette**: `AnimatePresence` with scale/fade transitions
- **List items**: `initial={{ opacity: 0, y: 8 }}` → `animate={{ opacity: 1, y: 0 }}` with `transition.delay` based on index
- **Sidebar labels**: `AnimatePresence` for collapse/expand text animation
- **Workspace messages**: Chat bubble entrance animation

### Reduced Motion

The `reducedMotion` user preference (stored in settings and user preferences) can be used to disable animations. Framer Motion respects `prefers-reduced-motion` at the browser level. Further, Tailwind's `motion-safe:` and `motion-reduce:` variants can be applied to animation classes.

## Status Colors Mapping

| UI State | Status Token | Examples |
|---|---|---|
| Operational | `status-success` | System healthy, agent active, task complete |
| Warning | `status-warning` | Degraded service, busy agent, paused automation |
| Error | `status-error` | Platform critical, agent error, failed workflow |
| Info | `status-info` | Running, processing, new information |
| Inactive | `status-pending` | Idle agent, pending task |

## Component Variants

### Button
- `variant`: `"default"` (primary filled) | `"outline"` | `"ghost"` | `"destructive"` | `"link"`
- `size`: `"default"` | `"sm"` | `"lg"` | `"icon"`

### Badge
- `variant`: `"default"` (primary filled) | `"outline"` | `"secondary"`

### Card
- Composed: `Card` → `CardHeader` → `CardTitle` + `CardDescription` → `CardContent`
- No variant prop; styling via className

## Theming Approach

Theming is achieved through CSS custom properties with class-based switching:

1. **Root variables** (`:root`) define light theme HSL values
2. **`.dark` class** overrides variables for dark theme
3. **System preference**: `prefers-color-scheme: dark` media query drives initial theme
4. **Toggle**: User selection via dropdown menu (light / dark / system)
5. **Persistence**: Theme preference stored in `useAppStore` (Zustand)
6. **Application**: `ClientLayout` applies/removes `dark` class on `<html>` element

```typescript
useEffect(() => {
  if (theme === "dark") root.classList.add("dark");
  else if (theme === "light") root.classList.remove("dark");
  else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", prefersDark);
  }
}, [theme]);
```

### Future: CSS Variable-Driven Themes

The architecture supports adding new themes by defining additional CSS variable blocks (e.g., `.high-contrast`, `.sepia`) without changing component code. All component styles reference variables, not hardcoded values.
