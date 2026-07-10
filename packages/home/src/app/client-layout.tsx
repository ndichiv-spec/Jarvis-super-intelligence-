"use client";

import { useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { useAppStore } from "@/stores/app-store";
import { LoadingScreen } from "@/components/shared/loading-screen";
import { OfflineScreen } from "@/components/shared/offline-screen";
import { useStartup } from "@/hooks/use-startup";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const { theme } = useAppStore();
  const { stage, events, error } = useStartup();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else if (theme === "light") {
      root.classList.remove("dark");
    } else {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.classList.toggle("dark", prefersDark);
    }
  }, [theme]);

  if (stage === "error" || stage === "timeout") {
    return <OfflineScreen events={events} error={error} stage={stage} />;
  }

  if (stage !== "ready") {
    return <LoadingScreen stage={stage} events={events} />;
  }

  return <MainLayout>{children}</MainLayout>;
}
