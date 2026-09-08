"use client";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { ConnectionBanner } from "@/components/connection-banner";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <ConnectionBanner />
      <DashboardShell>
        {children}
      </DashboardShell>
    </>
  );
}
