"use client";

import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  LayoutDashboard,
  Shield,
  RefreshCw,
  FileUp,
  Puzzle,
  Bell,
  Wifi,
  Download,
  Activity,
  ScrollText,
  Settings,
  PanelLeft,
  type LucideIcon,
} from "lucide-react";

interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
  section: string;
}

const navItems: NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, section: "overview" },
  { id: "permissions", label: "Permission Center", icon: Shield, section: "security" },
  { id: "sync", label: "Workspace Sync", icon: RefreshCw, section: "data" },
  { id: "file-interaction", label: "File Operations", icon: FileUp, section: "data" },
  { id: "integrations", label: "Integrations", icon: Puzzle, section: "extensions" },
  { id: "notifications", label: "Notifications", icon: Bell, section: "communication" },
  { id: "offline-mode", label: "Offline Mode", icon: Wifi, section: "system" },
  { id: "updates", label: "Updates", icon: Download, section: "system" },
  { id: "diagnostics", label: "Diagnostics", icon: Activity, section: "system" },
  { id: "audit", label: "Audit Log", icon: ScrollText, section: "security" },
  { id: "settings", label: "Settings", icon: Settings, section: "system" },
];

export function Sidebar() {
  const { activePage, setActivePage } = useDesktopStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-desktop-border bg-desktop-sidebar transition-all duration-200",
        sidebarOpen ? "w-56" : "w-12",
      )}
    >
      <div className="flex items-center justify-between h-10 px-3 border-b border-desktop-border">
        {sidebarOpen && (
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Desktop</span>
        )}
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={toggleSidebar}>
          <PanelLeft className="h-3.5 w-3.5" />
        </Button>
      </div>

      <TooltipProvider delayDuration={300}>
        <nav className="flex-1 py-2 space-y-0.5 overflow-y-auto scrollbar-thin">
          {navItems.map((item) => {
            const isActive = activePage === item.id;
            return (
              <Tooltip key={item.id}>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => setActivePage(item.id)}
                    className={cn(
                      "flex items-center w-full h-8 px-3 text-xs transition-colors",
                      sidebarOpen ? "gap-2" : "justify-center",
                      isActive
                        ? "bg-accent text-accent-foreground font-medium"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {sidebarOpen && <span className="truncate">{item.label}</span>}
                  </button>
                </TooltipTrigger>
                {!sidebarOpen && (
                  <TooltipContent side="right" className="text-xs">
                    {item.label}
                  </TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </nav>
      </TooltipProvider>
    </aside>
  );
}
