"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { StatusDot } from "@/components/shared/status-dot";
import { EmptyState } from "@/components/shared/empty-state";
import { Wrench, Search, Activity, Clock, ArrowUpRight } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { motion } from "framer-motion";

const tools = [
  { id: "1", name: "Web Search", description: "Search the web for information", category: "Search", status: "available" as const, executionCount: 1250, lastUsed: new Date(Date.now() - 3600000) },
  { id: "2", name: "Code Executor", description: "Execute code in a sandboxed environment", category: "Development", status: "available" as const, executionCount: 892, lastUsed: new Date(Date.now() - 7200000) },
  { id: "3", name: "File Reader", description: "Read and parse files of various formats", category: "Utilities", status: "available" as const, executionCount: 567, lastUsed: new Date(Date.now() - 14400000) },
  { id: "4", name: "Data Visualizer", description: "Create charts and visualizations from data", category: "Analysis", status: "busy" as const, executionCount: 234, lastUsed: new Date(Date.now() - 600000) },
  { id: "5", name: "API Client", description: "Make HTTP requests to external APIs", category: "Integration", status: "available" as const, executionCount: 423, lastUsed: new Date(Date.now() - 43200000) },
  { id: "6", name: "Template Engine", description: "Process and render templates", category: "Utilities", status: "available" as const, executionCount: 189, lastUsed: new Date(Date.now() - 86400000) },
  { id: "7", name: "Image Processor", description: "Analyze and transform images", category: "Media", status: "error" as const, executionCount: 56, lastUsed: new Date(Date.now() - 172800000) },
  { id: "8", name: "Database Query", description: "Execute read-only database queries", category: "Data", status: "disabled" as const, executionCount: 0, lastUsed: undefined },
];

const statusColors: Record<string, string> = {
  available: "bg-status-success/10 text-status-success border-status-success/20",
  busy: "bg-status-warning/10 text-status-warning border-status-warning/20",
  error: "bg-status-error/10 text-status-error border-status-error/20",
  disabled: "bg-muted text-muted-foreground",
};

const categories = Array.from(new Set(tools.map((t) => t.category)));

export default function ToolsPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  const filtered = tools.filter((t) => {
    if (category !== "All" && t.category !== category) return false;
    if (search && !t.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="pb-8">
      <PageHeader title="Tool Center" description="Browse and monitor available tools" />

      <div className="px-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Search tools..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-9" />
          </div>
          <div className="flex gap-1">
            <Badge variant={category === "All" ? "default" : "outline"} className="cursor-pointer" onClick={() => setCategory("All")}>All</Badge>
            {categories.map((c) => (
              <Badge key={c} variant={category === c ? "default" : "outline"} className="cursor-pointer" onClick={() => setCategory(c)}>{c}</Badge>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <EmptyState icon={Wrench} title="No tools found" description="Try a different search term" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((tool, i) => (
              <motion.div
                key={tool.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                          <Wrench className="h-4 w-4 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-sm">{tool.name}</CardTitle>
                          <p className="text-xs text-muted-foreground">{tool.description}</p>
                        </div>
                      </div>
                      <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <Badge variant="outline" className={statusColors[tool.status]}>
                        <StatusDot status={tool.status === "available" ? "success" : tool.status === "busy" ? "busy" : tool.status === "error" ? "error" : "inactive"} className="mr-1" />
                        {tool.status}
                      </Badge>
                      <Badge variant="secondary" className="text-[10px]">{tool.category}</Badge>
                    </div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><Activity className="h-3 w-3" />{tool.executionCount} runs</span>
                      {tool.lastUsed && <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{formatRelativeTime(tool.lastUsed)}</span>}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
