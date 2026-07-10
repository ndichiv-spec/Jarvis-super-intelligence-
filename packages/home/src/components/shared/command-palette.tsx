"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Search, MessageSquare, FolderKanban, Brain, BookOpen, Zap, Bot, Wrench, Puzzle, Bell, Settings, User, LayoutDashboard, Command } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { useKeyboardShortcut } from "@/hooks/use-keyboard";
import { motion, AnimatePresence } from "framer-motion";

interface CommandItem {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  href: string;
  category: string;
}

const commands: CommandItem[] = [
  { id: "home", label: "Home", description: "Go to dashboard", icon: LayoutDashboard, href: "/", category: "Navigation" },
  { id: "workspace", label: "AI Workspace", description: "Open conversational workspace", icon: MessageSquare, href: "/workspace", category: "Navigation" },
  { id: "projects", label: "Projects", description: "Manage projects", icon: FolderKanban, href: "/projects", category: "Navigation" },
  { id: "memory", label: "Memory Center", description: "View memories", icon: Brain, href: "/memory", category: "Navigation" },
  { id: "knowledge", label: "Knowledge Center", description: "Browse knowledge", icon: BookOpen, href: "/knowledge", category: "Navigation" },
  { id: "automation", label: "Automation Center", description: "Manage automations", icon: Zap, href: "/automation", category: "Navigation" },
  { id: "agents", label: "Agent Center", description: "Monitor agents", icon: Bot, href: "/agents", category: "Navigation" },
  { id: "tools", label: "Tool Center", description: "Browse tools", icon: Wrench, href: "/tools", category: "Navigation" },
  { id: "extensions", label: "Extension Center", description: "Manage extensions", icon: Puzzle, href: "/extensions", category: "Navigation" },
  { id: "notifications", label: "Notifications", description: "View notifications", icon: Bell, href: "/notifications", category: "Navigation" },
  { id: "search", label: "Search", description: "Search ecosystem", icon: Search, href: "/search", category: "Navigation" },
  { id: "profile", label: "Profile", description: "Manage profile", icon: User, href: "/profile", category: "Navigation" },
  { id: "settings", label: "Settings", description: "Configure platform", icon: Settings, href: "/settings", category: "Navigation" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useKeyboardShortcut([
    { key: "k", meta: true, handler: () => setOpen((prev) => !prev) },
    { key: "Escape", handler: () => { if (open) setOpen(false); } },
  ]);

  const filtered = query
    ? commands.filter(
        (c) =>
          c.label.toLowerCase().includes(query.toLowerCase()) ||
          c.description.toLowerCase().includes(query.toLowerCase()),
      )
    : commands;

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
    }
  }, [open]);

  const executeCommand = useCallback(
    (item: CommandItem) => {
      setOpen(false);
      router.push(item.href);
    },
    [router],
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % filtered.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length);
    } else if (e.key === "Enter" && filtered[selectedIndex]) {
      e.preventDefault();
      executeCommand(filtered[selectedIndex]);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: -20 }}
            className="fixed top-[15%] left-1/2 -translate-x-1/2 w-full max-w-lg z-50"
          >
            <div className="rounded-xl border bg-background shadow-2xl overflow-hidden">
              <div className="flex items-center gap-3 border-b px-4">
                <Search className="h-5 w-5 text-muted-foreground shrink-0" />
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Search pages and actions..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 h-12 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
                />
                <kbd className="hidden sm:inline-flex h-6 items-center gap-1 rounded border bg-muted px-2 text-[10px] font-medium text-muted-foreground">
                  <Command className="h-3 w-3" />K
                </kbd>
              </div>
              <div className="max-h-72 overflow-y-auto p-2">
                {filtered.length === 0 ? (
                  <p className="py-6 text-center text-sm text-muted-foreground">
                    No results for &ldquo;{query}&rdquo;
                  </p>
                ) : (
                  <div className="space-y-0.5">
                    {filtered.map((item, i) => (
                      <button
                        key={item.id}
                        onClick={() => executeCommand(item)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                          i === selectedIndex ? "bg-accent" : "hover:bg-accent/50",
                        )}
                      >
                        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
                          <item.icon className="h-4 w-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{item.label}</p>
                          <p className="text-xs text-muted-foreground truncate">{item.description}</p>
                        </div>
                        <span className="text-[10px] text-muted-foreground">{item.category}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
