"use client";

import { useEffect } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { useAppStore } from "@/stores/app-store";
import { LoadingScreen } from "@/components/shared/loading-screen";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const { loading, theme } = useAppStore();

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

  if (loading) return <LoadingScreen />;

  return <MainLayout>{children}</MainLayout>;
}
