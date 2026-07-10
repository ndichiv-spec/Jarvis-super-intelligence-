# Developer Guide

## Setup

```bash
cd packages/home
npm install
```

## Development

```bash
npm run dev
```

Starts Next.js dev server on `http://localhost:3000`.

## Build

```bash
npm run build
npm run start
```

## Testing

```bash
npm test            # Run all unit tests
npm run test:watch  # Watch mode
npm run test:e2e    # Playwright E2E tests
npm run test:a11y   # Accessibility tests
```

## Type Checking

```bash
npm run typecheck
```

## Linting

```bash
npm run lint
```

## Project Structure

```
src/
  app/              # Next.js App Router pages (13 routes)
  components/
    layout/         # Layout shell (sidebar, header, main-layout)
    shared/         # Reusable UI components
    ui/             # shadcn/ui primitives
    workspace/      # Workspace-specific components
  hooks/            # Custom React hooks
  lib/              # Utilities and API client
  stores/           # Zustand state management
  types/            # TypeScript interfaces
tests/
  unit/             # Unit tests (Vitest)
  e2e/              # E2E tests (Playwright)
docs/               # Documentation
```

## Adding a New Page

1. Create `src/app/<name>/page.tsx` with `"use client"` directive
2. Add navigation link in `src/components/layout/sidebar.tsx`
3. Add type in `src/types/index.ts` if new data model needed
4. Add API endpoint in `src/lib/api.ts` if needed
5. Add store state in `src/stores/app-store.ts` if needed
6. Write tests in `tests/unit/`

## Adding a New Component

1. Create file in `src/components/shared/` or appropriate directory
2. Follow existing patterns (props interface, cn() utility, shadcn/ui primitives)
3. Add to `COMPONENT_CATALOG.md`
4. Write tests in `tests/unit/components/`

## API Integration Pattern

```typescript
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";

function MyComponent() {
  const { data, isLoading, error, execute } = useApi(() => api.projects.list());

  if (isLoading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} onRetry={execute} />;
  if (!data?.length) return <EmptyState title="No projects" />;

  return <div>{/* render data */}</div>;
}
```

## State Management Pattern

```typescript
import { useAppStore } from "@/stores/app-store";

function MyComponent() {
  const { user, theme, setTheme } = useAppStore();
  // Access and mutate global state
}
```

## Key Commands

| Command | Action |
|---------|--------|
| `Cmd+K` | Open Command Palette |
| `Shift+?` | Show keyboard shortcuts |
| `Escape` | Close overlays |

## Deployment

```bash
npm run build
# Output in .next/ directory (standalone mode)
# Deploy to Azure Container Apps or similar
```
