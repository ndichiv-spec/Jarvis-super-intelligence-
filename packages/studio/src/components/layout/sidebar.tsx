"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import {
  LayoutDashboard,
  Bot,
  GitBranch,
  Wrench,
  Puzzle,
  BookOpen,
  Brain,
  PlayCircle,
  Radio,
  Cpu,
  Shield,
  Server,
  BarChart3,
  BookType,
  Settings,
  Terminal,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { motion, AnimatePresence } from "framer-motion";

interface NavSection {
  label: string;
  items: NavItem[];
}

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
}

const navSections: NavSection[] = [
  {
    label: "Overview",
    items: [
      { href: "/studio", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    label: "Design",
    items: [
      { href: "/studio/workspace", label: "Workspace Manager", icon: LayoutDashboard },
      { href: "/studio/agents", label: "Agent Designer", icon: Bot },
      { href: "/studio/workflows", label: "Workflow Designer", icon: GitBranch },
      { href: "/studio/tools", label: "Tool Manager", icon: Wrench },
      { href: "/studio/extensions", label: "Extension Manager", icon: Puzzle },
    ],
  },
  {
    label: "Knowledge",
    items: [
      { href: "/studio/knowledge", label: "Knowledge Explorer", icon: BookOpen },
      { href: "/studio/memory", label: "Memory Inspector", icon: Brain },
    ],
  },
  {
    label: "Observe",
    items: [
      { href: "/studio/automation", label: "Automation Monitor", icon: PlayCircle },
      { href: "/studio/events", label: "Event Monitor", icon: Radio },
    ],
  },
  {
    label: "Manage",
    items: [
      { href: "/studio/ai", label: "AI Runtime Manager", icon: Cpu },
      { href: "/studio/security", label: "Security Center", icon: Shield },
      { href: "/studio/infrastructure", label: "Infrastructure Monitor", icon: Server },
    ],
  },
  {
    label: "Analyze",
    items: [
      { href: "/studio/observability", label: "Observability Center", icon: BarChart3 },
    ],
  },
  {
    label: "Develop",
    items: [
      { href: "/studio/api-explorer", label: "API Explorer", icon: BookType },
      { href: "/studio/config", label: "Configuration Center", icon: Settings },
      { href: "/studio/console", label: "Developer Console", icon: Terminal },
    ],
  },
];

function NavLink({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  const pathname = usePathname();
  const isActive = pathname === item.href || (item.href !== "/studio" && pathname.startsWith(item.href));

  return (
    <Tooltip delayDuration={collapsed ? 100 : 99999}>
      <TooltipTrigger asChild>
        <Link
          href={item.href}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
            isActive
              ? "bg-sidebar-active/10 text-sidebar-active"
              : "text-sidebar-foreground hover:bg-accent hover:text-accent-foreground",
            collapsed && "justify-center px-2",
          )}
        >
          <item.icon className="h-4 w-4 shrink-0" />
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden whitespace-nowrap"
              >
                {item.label}
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </TooltipTrigger>
      {collapsed && <TooltipContent side="right">{item.label}</TooltipContent>}
    </Tooltip>
  );
}

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <TooltipProvider>
      <aside
        className={cn(
          "flex flex-col border-r bg-sidebar transition-all duration-200 z-10",
          sidebarCollapsed ? "w-14" : "w-56",
        )}
      >
        <div className={cn("flex h-12 items-center border-b px-3", sidebarCollapsed && "justify-center px-0")}>
          {!sidebarCollapsed ? (
            <Link href="/studio" className="flex items-center gap-2 font-semibold">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">
                JS
              </div>
              <span className="text-xs font-semibold">JARVIS Studio</span>
            </Link>
          ) : (
            <Link href="/studio" className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-[10px] font-bold text-primary-foreground">
              JS
            </Link>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
          {navSections.map((section) => (
            <div key={section.label} className="mb-3">
              {!sidebarCollapsed && (
                <p className="px-3 py-1 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                  {section.label}
                </p>
              )}
              <nav className="flex flex-col gap-0.5">
                {section.items.map((item) => (
                  <NavLink key={item.href} item={item} collapsed={sidebarCollapsed} />
                ))}
              </nav>
            </div>
          ))}
        </div>

        <button
          onClick={toggleSidebar}
          className="hidden lg:flex items-center justify-center h-7 border-t text-muted-foreground hover:text-foreground transition-colors"
        >
          {sidebarCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
        </button>
      </aside>
    </TooltipProvider>
  );
}
