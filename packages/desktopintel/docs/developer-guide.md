# Developer Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Rust | 1.77+ | Backend compilation |
| Node.js | 18+ | Frontend tooling |
| pnpm / npm | latest | Package management |
| Tauri CLI | 2.x | Desktop build tooling |
| Cargo | latest | Rust package management |

### Install Tauri CLI

```bash
cargo install tauri-cli --version "^2"
```

Or use npm:

```bash
npm install -g @tauri-apps/cli@^2
```

### Platform Dependencies

**Windows**: [Microsoft Visual Studio C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) (included in Windows 10 1803+)

**macOS**: Xcode Command Line Tools (`xcode-select --install`)

**Linux**: `libwebkit2gtk-4.1-dev`, `libappindicator3-dev`, `librsvg2-dev`, `patchelf`

## Setup Instructions

```bash
# Clone and enter the project
cd packages/desktopintel

# Install Node.js dependencies
npm install

# Rust dependencies are fetched automatically on first build
```

## Development Workflow

### Start Development Server

```bash
npm run tauri:dev
```

This launches:

1. A Vite/Next.js dev server (port 5432) for the frontend
2. The Tauri window pointing to the dev server
3. Hot-reload for both Rust and React code

### Frontend-Only Development

The frontend can run standalone in a browser for UI development:

```bash
npm run dev    # Next.js on localhost:5432
```

In browser mode, all Tauri `invoke()` calls fall back to mock data (see `src/lib/commands.ts`).

## Build Pipeline

```bash
# Production build
npm run tauri:build

# Output locations:
#   Windows: src-tauri/target/release/bundle/msi/
#   macOS:   src-tauri/target/release/bundle/dmg/
#   Linux:   src-tauri/target/release/bundle/appimage/
```

Run all checks before building:

```bash
npm run typecheck    # TypeScript type checking
npm run lint         # ESLint
npm run test         # Vitest
cargo clippy         # Rust linting (from src-tauri/)
```

## Project Structure

```
packages/desktopintel/
├── src/                          # Frontend (Next.js + React)
│   ├── app/
│   │   ├── (pages)/              # Page components
│   │   │   ├── audit.tsx
│   │   │   ├── dashboard.tsx
│   │   │   ├── diagnostics.tsx
│   │   │   ├── file-interaction.tsx
│   │   │   ├── integrations.tsx
│   │   │   ├── notifications.tsx
│   │   │   ├── offline-mode.tsx
│   │   │   ├── permissions.tsx
│   │   │   ├── settings.tsx
│   │   │   ├── sync.tsx
│   │   │   └── updates.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── layout/               # Layout components
│   │   │   ├── command-palette.tsx
│   │   │   ├── main-layout.tsx
│   │   │   ├── notification-panel.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── titlebar.tsx
│   │   ├── shared/               # Shared components
│   │   │   ├── data-table.tsx
│   │   │   ├── empty-state.tsx
│   │   │   ├── section-header.tsx
│   │   │   ├── stat-card.tsx
│   │   │   └── status-dot.tsx
│   │   └── ui/                   # Primitive UI components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       └── ... (Radix-based)
│   ├── lib/
│   │   ├── commands.ts           # Tauri invoke wrappers + mocks
│   │   └── utils.ts              # Shared utilities
│   ├── stores/
│   │   ├── desktop-store.ts      # Zustand global state
│   │   └── ui-store.ts           # UI-specific state
│   └── types/
│       └── index.ts              # TypeScript type definitions
├── src-tauri/
│   ├── src/
│   │   ├── main.rs               # Entry point
│   │   ├── lib.rs                # Tauri builder, plugin/state/command registration
│   │   ├── audit/mod.rs
│   │   ├── diagnostics/mod.rs
│   │   ├── file_interaction/mod.rs
│   │   ├── integrations/mod.rs
│   │   ├── notifications/mod.rs
│   │   ├── offline/mod.rs
│   │   ├── palette/mod.rs
│   │   ├── permissions/mod.rs
│   │   ├── runtime/mod.rs
│   │   ├── settings/mod.rs
│   │   ├── sync/mod.rs
│   │   └── updates/mod.rs
│   ├── build.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
├── tests/                        # Test files
├── package.json
├── tsconfig.json
└── vitest.config.ts
```

## Adding a New Tauri Command

### 1. Add the command in the appropriate Rust module

```rust
// src-tauri/src/my_module/mod.rs
#[tauri::command]
pub fn my_command(state: tauri::State<'_, MyState>) -> MyResult {
    state.do_something()
}
```

### 2. Register the command in `lib.rs`

```rust
// src-tauri/src/lib.rs
.invoke_handler(tauri::generate_handler![
    // ... existing commands
    my_module::my_command,
])
```

### 3. Add a TypeScript wrapper in `commands.ts`

```typescript
// src/lib/commands.ts
export const commands = {
  // ... existing
  myCommand: () => invoke<MyResult>("my_command"),
};
```

### 4. Add mock data in `commands.ts`

```typescript
function getMockData(cmd: string): unknown {
  const mocks: Record<string, unknown> = {
    // ...
    my_command: { /* mock response */ },
  };
}
```

### 5. Add types if needed

```typescript
// src/types/index.ts
export interface MyResult { ... }
```

## Adding a New Page/Component

### 1. Create the page file

```typescript
// src/app/(pages)/my-page.tsx
"use client";
import { MainLayout } from "@/components/layout/main-layout";

export default function MyPage() {
  return (
    <MainLayout activePage="my-page">
      {/* page content */}
    </MainLayout>
  );
}
```

### 2. Add the route in the sidebar

```typescript
// src/components/layout/sidebar.tsx
{ label: "My Page", value: "my-page", icon: SomeIcon }
```

### 3. Add the page to the store

```typescript
// desktop-store.ts — add to refreshAll() if needed
```

## State Management Patterns

The application uses **Zustand** for state management:

### Reading State

```typescript
import { useDesktopStore } from "@/stores/desktop-store";

function MyComponent() {
  const syncStatus = useDesktopStore((s) => s.state.sync);
  const triggerSync = useDesktopStore((s) => s.triggerSync);
  // ...
}
```

### Mutating State

All mutations go through Tauri commands. The store dispatches the command and updates local state on success:

```typescript
triggerSync: async () => {
  await commands.triggerSync();
  const sync = await commands.getSyncStatus();
  set((s) => ({ state: { ...s.state, sync } }));
},
```

### Initialization

The `initialize()` method fires 15 parallel `invoke()` calls to populate all state on app start:

```typescript
initialize: async () => {
  const [runtime, permissions, sync, ...] = await Promise.all([
    commands.getRuntimeStatus(),
    commands.getPermissions(),
    // ...
  ]);
  set({ state: { runtime, permissions, sync, ... } });
},
```

## Testing Patterns

### Frontend Tests (Vitest)

```typescript
// Component test example
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";

describe("StatusDot", () => {
  it("renders with correct color for synced state", () => {
    render(<StatusDot state="synced" />);
    expect(screen.getByRole("status")).toHaveClass("bg-green-500");
  });
});
```

### Rust Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_permission_lifecycle() {
        let pc = PermissionCenter::new();
        let req = pc.request(PermissionType::FileSystemRead, "testing");
        assert_eq!(req.status, RequestStatus::Pending);

        let grant = pc.grant(&req.id).unwrap();
        assert_eq!(grant.permission_type, PermissionType::FileSystemRead);
    }
}
```

## Integration with Service Gateway

The desktop communicates with the JARVIS Service Gateway via HTTP (reqwest):

- **Sync data** is pushed/pulled via REST endpoints
- **Gateway connectivity** is tracked in `RuntimeState.gateway_connected`
- **Updates** are checked via the Gateway's update endpoint

Configure the Gateway URL via settings (future: `GeneralSettings.gateway_url`).

## Debugging Tips

| Issue | Debug Method |
|-------|-------------|
| Rust panic | Set `RUST_BACKTRACE=1` before `npm run tauri:dev` |
| Frontend errors | Open browser DevTools (F12) in the Tauri window |
| IPC issues | Enable Tauri logging: `RUST_LOG=info` |
| State issues | Check Zustand DevTools extension |
| Build errors | `cargo build` from `src-tauri/` for Rust-only errors |
| Mock vs real | Check `isTauri` flag in `commands.ts` |
| Tauri config | Inspect `src-tauri/tauri.conf.json` for window, bundle, security settings |
