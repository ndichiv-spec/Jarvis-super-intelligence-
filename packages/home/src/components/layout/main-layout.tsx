"use client";

import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { useAppStore } from "@/stores/app-store";
import { useEffect } from "react";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, setUser } = useAppStore();

  useEffect(() => {
    if (!user) {
      setUser({
        id: "user-1",
        name: "Alex Chen",
        email: "alex@example.com",
        role: "Developer",
        preferences: {
          theme: "system" as const,
          sidebarCollapsed: false,
          fontSize: "medium" as const,
          reducedMotion: false,
        },
      });
    }
  }, [user, setUser]);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto scrollbar-thin">
          {children}
        </main>
      </div>
    </div>
  );
}
