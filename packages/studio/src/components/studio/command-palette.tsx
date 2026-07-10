"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, Bot, GitBranch, LayoutDashboard, Wrench, Puzzle, BookOpen, Brain, PlayCircle, Radio, Cpu, Shield, Server, BarChart3, BookType, Settings, Terminal, Command, ArrowRight } from "lucide-react";
import { Command as CommandPrimitive } from "cmdk";
import { Dialog, DialogContent } from "@/components/ui/dialog";

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  href?: string;
  action?: () => void;
  category: string;
  icon: React.ElementType;
}

const iconMap: Record<string, React.ElementType> = {
  Bot, GitBranch, LayoutDashboard, Wrench, Puzzle, BookOpen, Brain,
  PlayCircle, Radio, Cpu, Shield, Server, BarChart3, BookType, Settings, Terminal,
};

const defaultCommands: CommandItem[] = [
  { id: "nav-dashboard", label: "Go to Dashboard", href: "/studio", category: "Navigation", icon: LayoutDashboard },
  { id: "nav-agents", label: "Open Agent Designer", href: "/studio/agents", category: "Navigation", icon: Bot },
  { id: "nav-workflows", label: "Open Workflow Designer", href: "/studio/workflows", category: "Navigation", icon: GitBranch },
  { id: "nav-tools", label: "Open Tool Manager", href: "/studio/tools", category: "Navigation", icon: Wrench },
  { id: "nav-extensions", label: "Open Extension Manager", href: "/studio/extensions", category: "Navigation", icon: Puzzle },
  { id: "nav-knowledge", label: "Open Knowledge Explorer", href: "/studio/knowledge", category: "Navigation", icon: BookOpen },
  { id: "nav-memory", label: "Open Memory Inspector", href: "/studio/memory", category: "Navigation", icon: Brain },
  { id: "nav-automation", label: "Open Automation Monitor", href: "/studio/automation", category: "Navigation", icon: PlayCircle },
  { id: "nav-events", label: "Open Event Monitor", href: "/studio/events", category: "Navigation", icon: Radio },
  { id: "nav-ai", label: "Open AI Runtime Manager", href: "/studio/ai", category: "Navigation", icon: Cpu },
  { id: "nav-security", label: "Open Security Center", href: "/studio/security", category: "Navigation", icon: Shield },
  { id: "nav-infra", label: "Open Infrastructure Monitor", href: "/studio/infrastructure", category: "Navigation", icon: Server },
  { id: "nav-observability", label: "Open Observability Center", href: "/studio/observability", category: "Navigation", icon: BarChart3 },
  { id: "nav-api", label: "Open API Explorer", href: "/studio/api-explorer", category: "Navigation", icon: BookType },
  { id: "nav-config", label: "Open Configuration Center", href: "/studio/config", category: "Navigation", icon: Settings },
  { id: "nav-console", label: "Open Developer Console", href: "/studio/console", category: "Navigation", icon: Terminal },
  { id: "nav-workspace", label: "Open Workspace Manager", href: "/studio/workspace", category: "Navigation", icon: LayoutDashboard },
];

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "p" && (e.metaKey || e.ctrlKey) && e.shiftKey) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const handleSelect = useCallback(
    (item: CommandItem) => {
      setOpen(false);
      setSearch("");
      if (item.href) router.push(item.href);
      else item.action?.();
    },
    [router],
  );

  const filtered = search
    ? defaultCommands.filter(
        (c) =>
          c.label.toLowerCase().includes(search.toLowerCase()) ||
          c.description?.toLowerCase().includes(search.toLowerCase()),
      )
    : defaultCommands;

  const grouped = filtered.reduce<Record<string, CommandItem[]>>((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {});

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="top-[15%] p-0 max-w-lg [&>button]:hidden">
        <CommandPrimitive className="rounded-lg border shadow-md">
          <div className="flex items-center border-b px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
            <CommandPrimitive.Input
              ref={inputRef}
              value={search}
              onValueChange={setSearch}
              placeholder="Type a command or search..."
              className="flex h-11 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            <kbd className="hidden sm:inline-flex items-center gap-1 rounded border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
              <Command className="h-2.5 w-2.5" />P
            </kbd>
          </div>
          <CommandPrimitive.List className="max-h-64 overflow-y-auto p-2">
            {Object.entries(grouped).map(([category, items]) => (
              <CommandPrimitive.Group key={category} heading={category}>
                {items.map((item) => (
                  <CommandPrimitive.Item
                    key={item.id}
                    value={item.id}
                    onSelect={() => handleSelect(item)}
                    className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground"
                  >
                    <item.icon className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="flex-1">{item.label}</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground opacity-0 group-data-[selected=true]:opacity-100" />
                  </CommandPrimitive.Item>
                ))}
              </CommandPrimitive.Group>
            ))}
            {filtered.length === 0 && (
              <div className="py-6 text-center text-sm text-muted-foreground">No results found.</div>
            )}
          </CommandPrimitive.List>
        </CommandPrimitive>
      </DialogContent>
    </Dialog>
  );
}
