"use client";

import { useEffect } from "react";
import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";
import { Sidebar } from "./sidebar";
import { Titlebar } from "./titlebar";
import { CommandPalette } from "./command-palette";
import { NotificationPanel } from "./notification-panel";
import { Dashboard } from "@/app/(pages)/dashboard";
import { PermissionCenter } from "@/app/(pages)/permissions";
import { WorkspaceSync } from "@/app/(pages)/sync";
import { FileInteraction } from "@/app/(pages)/file-interaction";
import { Integrations } from "@/app/(pages)/integrations";
import { NotificationsPage } from "@/app/(pages)/notifications";
import { OfflineMode } from "@/app/(pages)/offline-mode";
import { Updates } from "@/app/(pages)/updates";
import { Diagnostics } from "@/app/(pages)/diagnostics";
import { AuditLog } from "@/app/(pages)/audit";
import { SettingsPage } from "@/app/(pages)/settings";
import { ScrollArea } from "@/components/ui/scroll-area";

export function MainLayout() {
  const { initialize, activePage, state } = useDesktopStore();
  const { notificationPanelOpen, commandPaletteOpen } = useUIStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        useUIStore.getState().setCommandPaletteOpen(!commandPaletteOpen);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen]);

  const renderPage = () => {
    switch (activePage) {
      case "dashboard": return <Dashboard />;
      case "permissions": return <PermissionCenter />;
      case "sync": return <WorkspaceSync />;
      case "file-interaction": return <FileInteraction />;
      case "integrations": return <Integrations />;
      case "notifications": return <NotificationsPage />;
      case "offline-mode": return <OfflineMode />;
      case "updates": return <Updates />;
      case "diagnostics": return <Diagnostics />;
      case "audit": return <AuditLog />;
      case "settings": return <SettingsPage />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      <Titlebar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden bg-desktop-panel">
          <ScrollArea className="h-full">
            <div className="p-4">
              {renderPage()}
            </div>
          </ScrollArea>
        </main>
      </div>
      {commandPaletteOpen && <CommandPalette />}
      {notificationPanelOpen && <NotificationPanel />}
    </div>
  );
}
