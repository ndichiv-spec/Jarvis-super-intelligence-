# Design System

## CSS Custom Properties

Defined in `src/app/globals.css` under `:root` and `.dark` selectors. All UI components reference these variables.

### Color Tokens

| Variable | Light Value | Dark Value | Usage |
|---|---|---|---|
| `--background` | `0 0% 100%` | `222.2 84% 4.9%` | Page background |
| `--foreground` | `222.2 84% 4.9%` | `210 40% 98%` | Primary text |
| `--card` | `0 0% 100%` | `222.2 84% 4.9%` | Card/panel backgrounds |
| `--card-foreground` | `222.2 84% 4.9%` | `210 40% 98%` | Card text |
| `--popover` | `0 0% 100%` | `222.2 84% 4.9%` | Dropdown/popover bg |
| `--popover-foreground` | `222.2 84% 4.9%` | `210 40% 98%` | Popover text |
| `--primary` | `222.2 47.4% 11.2%` | `210 40% 98%` | Primary action bg |
| `--primary-foreground` | `210 40% 98%` | `222.2 47.4% 11.2%` | Primary action text |
| `--secondary` | `210 40% 96.1%` | `217.2 32.6% 17.5%` | Secondary action bg |
| `--secondary-foreground` | `222.2 47.4% 11.2%` | `210 40% 98%` | Secondary action text |
| `--muted` | `210 40% 96.1%` | `217.2 32.6% 17.5%` | Muted bg (search, disabled) |
| `--muted-foreground` | `215.4 16.3% 46.9%` | `215 20.2% 65.1%` | Muted/secondary text |
| `--accent` | `210 40% 96.1%` | `217.2 32.6% 17.5%` | Accent/hover bg |
| `--accent-foreground` | `222.2 47.4% 11.2%` | `210 40% 98%` | Accent text |
| `--destructive` | `0 100% 50%` | `0 62.8% 30.6%` | Destructive actions (delete) |
| `--destructive-foreground` | `210 40% 98%` | `210 40% 98%` | Destructive text |
| `--border` | `214.3 31.8% 91.4%` | `217.2 32.6% 17.5%` | Card/input borders |
| `--input` | `214.3 31.8% 91.4%` | `217.2 32.6% 17.5%` | Input field borders |
| `--ring` | `222.2 84% 4.9%` | `212.7 26.8% 83.9%` | Focus ring |
| `--radius` | `0.5rem` | `0.5rem` | Border radius base |

### Semantic Classes (globals.css)

```css
@layer base {
  * { @apply border-border; }
  body { @apply bg-background text-foreground; }
}
```

### Animation Keyframes

| Keyframe | Purpose |
|---|---|
| `accordion-up` / `accordion-down` | Radix Accordion slide |
| `collapsible-up` / `collapsible-down` | Radix Collapsible slide |
| `dialog-overlay-show` / `dialog-overlay-hide` | Dialog overlay fade |
| `dialog-content-show` / `dialog-content-hide` | Dialog content scale+fade |
| `dropdown-content-show` / `dropdown-content-hide` | Dropdown scale+fade |
| `pulse-dot` | StatusDot pulsing (opacity) |

### Prefers-Reduced-Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after { animation-duration: 0.01ms !important; }
}
```

## Status Colors

Status colors are defined as arbitrary Tailwind values to match the design intent. Applied via `StatusDot` `status` prop.

| Status Group | Tailwind Class |
|---|---|
| success / healthy / active / available / running | `bg-status-success` → `bg-[#22c55e]` |
| warning / degraded / busy / maintenance | `bg-status-warning` → `bg-[#eab308]` |
| pending / idle / draft | `bg-status-pending` → `bg-[#6b7280]` |
| error / critical / suspended | `bg-status-error` → `bg-[#ef4444]` |
| inactive / disabled / archived | `bg-muted-foreground` (varies per theme) |

## Typography

- **Font family**: `Inter` (imported via Google Fonts in `layout.tsx`)
- **Base size**: 14px (`text-sm` on `<html>`)
- **Monospace**: `tabular-nums` utility class for numerical data alignment in DataTable columns
- **Mono spans**: Used for API paths (`font-mono`), IDs, durations, IP addresses

## Tailwind Configuration

`tailwind.config.ts` extends the default theme with:

```ts
colors: {
  border: "hsl(var(--border))",
  input: "hsl(var(--input))",
  ring: "hsl(var(--ring))",
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary:   { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
  secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
  destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
  muted:    { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
  accent:   { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
  popover:  { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
  card:     { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
},
borderRadius: {
  xl: "calc(var(--radius) + 4px)",
  lg: "var(--radius)",
  md: "calc(var(--radius) - 2px)",
  sm: "calc(var(--radius) - 4px)",
},
keyframes: { /* animation keyframes */ },
animation: { /* animation references */ },
```

## Spacing & Layout

- **Sidebar width**: `w-56` (224px) expanded, `w-14` (56px) collapsed
- **Content padding**: `px-6` horizontal padding on main content
- **Card gaps**: `gap-3` grid for stat cards, `gap-4` for general card grids
- **Section spacing**: `space-y-6` between major sections
- **Table cell padding**: `px-4 py-3` in DataTable header, `px-4 py-2.5` in body rows

## Shadows

- **Card**: `shadow-sm` (default card)
- **Dropdown**: `shadow-md`
- **Dialog overlay**: default Radix overlay (translucent black)

## Component Sizing

- **StatCard badges**: `h-8 w-8` icon container, `h-4 w-4` icon
- **StatusDot**: `h-2 w-2` (standard), `h-3 w-3` (large via className override)
- **Avatar**: `h-8 w-8` (header), `h-9 w-9` (data table)
- **Icon buttons**: `h-8 w-8` button with `h-4 w-4` icon
- **Progress bar**: `h-2` height
- **Select trigger**: `w-[180px]` in workspace selector

## Framer Motion Variants

Used across workspace pages for staggered entrance animations:

```ts
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};
const itemVariants: Variants = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" } },
};
```

Applied as:
```tsx
<motion.div variants={containerVariants} initial="hidden" animate="visible">
  <motion.div variants={itemVariants}>...</motion.div>
</motion.div>
```

## Theme Preference

Theme toggling uses `next-themes`:
- Three modes: Light / Dark / System
- Toggle dropdown rendered in Header: sun icon (light), moon icon (dark), monitor icon (system)
- CSS variables in `.dark` class override for dark mode
- Developer Console log panel uses hardcoded `#0d1117` dark background independent of theme
