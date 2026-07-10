"use client";

import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { StatusBar } from "./status-bar";
import { CommandPalette } from "@/components/studio/command-palette";
import { GlobalSearch } from "@/components/studio/global-search";
import { useAppStore } from "@/stores/app-store";
import { useEffect } from "react";

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

interface ShellUser { id: string; name: string; email: string; role: string; organizationId?: string; }
interface ShellResponse {
  ok: boolean;
  data: {
    user: ShellUser | null;
    current_workspace: Record<string, unknown> | null;
    workspaces: Record<string, unknown>[];
    organizations: Record<string, unknown>[];
    notifications: Record<string, unknown>[];
  };
}

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { setUser, setLoading, setCurrentWorkspace, setOrganizations, setStats } = useAppStore();

  useEffect(() => {
    async function init() {
      try {
        const res = await fetch(`${GATEWAY_URL}/studio/shell`);
        if (res.ok) {
          const body: ShellResponse = await res.json();
          if (body.ok && body.data) {
            const { user, current_workspace, workspaces, organizations } = body.data;
            if (user) {
              setUser({
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role ?? "",
                organizationId: user.organizationId,
                preferences: {
                  theme: "system",
                  sidebarCollapsed: false,
                  fontSize: "medium",
                  reducedMotion: false,
                },
              });
            }
            if (current_workspace) {
              setCurrentWorkspace(current_workspace as never);
            }
            if (organizations) {
              setOrganizations(organizations as never);
            }
            const statsRes = await fetch(`${GATEWAY_URL}/studio/dashboard/stats`);
            if (statsRes.ok) {
              const statsBody = await statsRes.json();
              if (statsBody.ok) setStats(statsBody.data);
            }
          }
        }
      } catch {
        setUser({
          id: "user-1",
          name: "Alex Developer",
          email: "alex@jarvis.ai",
          role: "Engineering Lead",
          organizationId: "org-1",
          preferences: { theme: "system", sidebarCollapsed: false, fontSize: "medium", reducedMotion: false },
        });
        setCurrentWorkspace({
          id: "ws-1", name: "JARVIS Core", description: "Main development workspace",
          environment: "development", organizationId: "org-1", projectCount: 12, activeAgentCount: 8,
          lastActivity: new Date(),
        });
        setOrganizations([
          { id: "org-1", name: "JARVIS AI", slug: "jarvis-ai", description: "Primary organization", memberCount: 24, workspaceCount: 3 },
        ]);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [setUser, setLoading, setCurrentWorkspace, setOrganizations, setStats]);

  return (
    <div className="flex h-screen overflow-hidden bg-studio-bg">
      <CommandPalette />
      <GlobalSearch />
      <Sidebar />
      <div className="flex flex-1 flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto scrollbar-thin">
          {children}
        </main>
        <StatusBar />
      </div>
    </div>
  );
}
