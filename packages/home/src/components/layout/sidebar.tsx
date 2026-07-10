"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import {
  LayoutDashboard,
  MessageSquare,
  FolderKanban,
  Brain,
  BookOpen,
  Zap,
  Bot,
  Wrench,
  Puzzle,
  Bell,
  Search,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Radio,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { motion, AnimatePresence } from "framer-motion";

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

const navItems: NavItem[] = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/workspace", label: "AI Workspace", icon: MessageSquare },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/memory", label: "Memory Center", icon: Brain },
  { href: "/knowledge", label: "Knowledge Center", icon: BookOpen },
  { href: "/automation", label: "Automation", icon: Zap },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/intelligence", label: "Intelligence", icon: Cpu },
  { href: "/tools", label: "Tools", icon: Wrench },
  { href: "/extensions", label: "Extensions", icon: Puzzle },
  { href: "/communication", label: "Communication", icon: Radio },
];

const bottomItems: NavItem[] = [
  { href: "/notifications", label: "Notifications", icon: Bell },
  { href: "/search", label: "Search", icon: Search },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

function NavLink({
  item,
  collapsed,
}: {
  item: NavItem;
  collapsed: boolean;
}) {
  const pathname = usePathname();
  const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

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
          <item.icon className="h-5 w-5 shrink-0" />
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden"
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
  const { sidebarCollapsed, toggleSidebar, unreadCount } = useAppStore();

  return (
    <TooltipProvider>
      <aside
        className={cn(
          "flex flex-col border-r bg-sidebar transition-all duration-200",
          sidebarCollapsed ? "w-16" : "w-60",
        )}
      >
        <div className={cn("flex h-14 items-center border-b px-4", sidebarCollapsed && "justify-center px-0")}>
          {!sidebarCollapsed && (
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
                J
              </div>
              <span className="text-sm">JARVIS Home</span>
            </Link>
          )}
          {sidebarCollapsed && (
            <Link href="/" className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
              J
            </Link>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
          <nav className="flex flex-col gap-1">
            {navItems.map((item) => (
              <NavLink key={item.href} item={item} collapsed={sidebarCollapsed} />
            ))}
          </nav>
        </div>

        <div className="border-t p-2">
          <nav className="flex flex-col gap-1">
            {bottomItems.map((item) => (
              <div key={item.href} className="relative">
                <NavLink item={item} collapsed={sidebarCollapsed} />
                {item.href === "/notifications" && unreadCount > 0 && (
                  <span className={cn(
                    "absolute top-1 right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-error text-[10px] font-medium text-white px-1",
                    sidebarCollapsed && "right-0.5 top-0.5",
                  )}>
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                )}
              </div>
            ))}
          </nav>
        </div>

        <button
          onClick={toggleSidebar}
          className="hidden lg:flex items-center justify-center h-8 border-t text-muted-foreground hover:text-foreground transition-colors"
        >
          {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </aside>
    </TooltipProvider>
  );
}
