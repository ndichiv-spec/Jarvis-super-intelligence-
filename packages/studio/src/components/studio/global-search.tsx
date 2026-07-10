"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, File, Bot, BookOpen, Brain, Wrench, GitBranch, ArrowRight } from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";

interface SearchResult {
  id: string;
  title: string;
  description: string;
  href: string;
  type: "agent" | "workflow" | "knowledge" | "memory" | "tool" | "extension";
  icon: React.ElementType;
}

const mockResults: SearchResult[] = [
  { id: "s1", title: "PlannerAgent", description: "Strategic planning and task decomposition", href: "/studio/agents", type: "agent", icon: Bot },
  { id: "s2", title: "CodingAgent", description: "Code generation and analysis", href: "/studio/agents", type: "agent", icon: Bot },
  { id: "s3", title: "ResearchAgent", description: "Web research and information gathering", href: "/studio/agents", type: "agent", icon: Bot },
  { id: "s4", title: "Data Pipeline", description: "End-to-end data processing workflow", href: "/studio/workflows", type: "workflow", icon: GitBranch },
  { id: "s5", title: "Code Review", description: "Automated code review workflow", href: "/studio/workflows", type: "workflow", icon: GitBranch },
  { id: "s6", title: "Research Papers", description: "Academic papers and publications collection", href: "/studio/knowledge", type: "knowledge", icon: BookOpen },
  { id: "s7", title: "Knowledge Graph", description: "Entity and relationship knowledge base", href: "/studio/knowledge", type: "knowledge", icon: BookOpen },
  { id: "s8", title: "User prefers dark mode", description: "Memory: preference stored from user feedback", href: "/studio/memory", type: "memory", icon: Brain },
  { id: "s9", title: "FileReader", description: "Read and parse file tool", href: "/studio/tools", type: "tool", icon: Wrench },
  { id: "s10", title: "WebScraper", description: "Extract data from web pages", href: "/studio/tools", type: "tool", icon: Wrench },
];

export function GlobalSearch() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const handleSelect = useCallback(
    (result: SearchResult) => {
      setOpen(false);
      setQuery("");
      router.push(result.href);
    },
    [router],
  );

  const filtered = query
    ? mockResults.filter(
        (r) =>
          r.title.toLowerCase().includes(query.toLowerCase()) ||
          r.description.toLowerCase().includes(query.toLowerCase()),
      )
    : mockResults;

  const grouped = filtered.reduce<Record<string, SearchResult[]>>((acc, item) => {
    if (!acc[item.type]) acc[item.type] = [];
    acc[item.type].push(item);
    return acc;
  }, {});

  const typeLabels: Record<string, string> = {
    agent: "Agents",
    workflow: "Workflows",
    knowledge: "Knowledge",
    memory: "Memory",
    tool: "Tools",
    extension: "Extensions",
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="top-[10%] p-0 max-w-xl [&>button]:hidden">
        <div className="rounded-lg border shadow-md">
          <div className="flex items-center border-b px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search agents, workflows, knowledge, memory..."
              className="flex h-11 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              autoFocus
            />
          </div>
          <div className="max-h-80 overflow-y-auto p-2">
            {Object.entries(grouped).map(([type, results]) => (
              <div key={type} className="mb-2">
                <p className="px-2 py-1 text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                  {typeLabels[type] || type}
                </p>
                {results.map((result) => (
                  <button
                    key={result.id}
                    onClick={() => handleSelect(result)}
                    className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground text-left"
                  >
                    <result.icon className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate">{result.title}</p>
                      <p className="text-[10px] text-muted-foreground truncate">{result.description}</p>
                    </div>
                    <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0 opacity-0 group-hover:opacity-100" />
                  </button>
                ))}
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="py-6 text-center text-sm text-muted-foreground">No results found.</div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
