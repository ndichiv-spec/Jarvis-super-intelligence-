"use client";

import { useState, useEffect, useRef } from "react";
import { useDesktopStore } from "@/stores/desktop-store";
import { useUIStore } from "@/stores/ui-store";
import { Search } from "lucide-react";

export function CommandPalette() {
  const { commands, setActivePage } = useDesktopStore();
  const { setCommandPaletteOpen } = useUIStore();
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const filtered = commands.filter(
    (c) =>
      c.title.toLowerCase().includes(query.toLowerCase()) ||
      c.description.toLowerCase().includes(query.toLowerCase()),
  );

  const handleSelect = (id: string) => {
    if (id.startsWith("nav-")) {
      const page = id.replace("nav-", "");
      setActivePage(page);
    }
    setCommandPaletteOpen(false);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      onClick={() => setCommandPaletteOpen(false)}
    >
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="relative w-full max-w-lg bg-background border border-border rounded-lg shadow-2xl overflow-hidden animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-3 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands..."
            className="flex-1 h-10 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="text-[10px] text-muted-foreground border border-border rounded px-1.5 py-0.5">ESC</kbd>
        </div>
        <div className="max-h-64 overflow-y-auto scrollbar-thin p-1">
          {filtered.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-6">No results found</p>
          ) : (
            filtered.map((cmd) => (
              <button
                key={cmd.id}
                className="flex items-center gap-2 w-full px-3 py-2 text-xs rounded-md hover:bg-accent transition-colors text-left"
                onClick={() => handleSelect(cmd.id)}
              >
                <span className="font-medium">{cmd.title}</span>
                <span className="text-muted-foreground ml-1">— {cmd.description}</span>
                {cmd.shortcut && (
                  <span className="ml-auto text-[10px] text-muted-foreground font-mono">{cmd.shortcut}</span>
                )}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
