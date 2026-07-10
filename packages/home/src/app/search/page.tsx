"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/empty-state";
import {
  Search,
  MessageSquare,
  FolderKanban,
  Brain,
  BookOpen,
  Bot,
  Wrench,
  Puzzle,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { motion } from "framer-motion";

interface SearchResult {
  id: string;
  type: "conversation" | "project" | "memory" | "knowledge" | "agent" | "tool" | "extension";
  title: string;
  description: string;
  url: string;
}

const typeConfig: Record<string, { icon: React.ElementType; color: string }> = {
  conversation: { icon: MessageSquare, color: "text-blue-500" },
  project: { icon: FolderKanban, color: "text-amber-500" },
  memory: { icon: Brain, color: "text-purple-500" },
  knowledge: { icon: BookOpen, color: "text-green-500" },
  agent: { icon: Bot, color: "text-cyan-500" },
  tool: { icon: Wrench, color: "text-orange-500" },
  extension: { icon: Puzzle, color: "text-pink-500" },
};

const popularSearches = ["Q2 analysis", "API documentation", "system architecture", "performance", "security audit"];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(false);

  const results: SearchResult[] = query
    ? [
        { id: "1", type: "conversation" as const, title: "Q2 Financial Analysis", description: "Conversation about Q2 financial metrics and trends", url: "/workspace" },
        { id: "2", type: "project" as const, title: "Market Analysis Q2", description: "Project for Q2 market analysis and competitor research", url: "/projects" },
        { id: "3", type: "knowledge" as const, title: "Q1 2026 Research Findings", description: "Compiled research data and insights from Q1", url: "/knowledge" },
        { id: "4", type: "memory" as const, title: "User prefers data visualization", description: "Memory about user's preference for visual data", url: "/memory" },
        { id: "5", type: "agent" as const, title: "DataAnalyzer", description: "AI agent specialized in data analysis and visualization", url: "/agents" },
        { id: "6", type: "tool" as const, title: "Data Visualizer", description: "Tool for creating charts and visualizations", url: "/tools" },
      ].filter((r) => r.title.toLowerCase().includes(query.toLowerCase()) || r.description.toLowerCase().includes(query.toLowerCase()))
    : [];

  const handleSearch = (q: string) => {
    setQuery(q);
    setSearched(true);
  };

  return (
    <div className="pb-8">
      <PageHeader title="Search" description="Search across your entire JARVIS ecosystem" />

      <div className="px-6 space-y-6">
        <div className="relative max-w-2xl mx-auto">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search conversations, projects, memory, knowledge, agents, tools..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-12 h-12 text-base"
            autoFocus
          />
        </div>

        {!query && !searched && (
          <div className="max-w-2xl mx-auto">
            <p className="text-sm text-muted-foreground mb-3">Popular searches</p>
            <div className="flex flex-wrap gap-2">
              {popularSearches.map((s) => (
                <Badge key={s} variant="secondary" className="cursor-pointer text-sm py-1.5" onClick={() => handleSearch(s)}>
                  <Sparkles className="h-3 w-3 mr-1" />
                  {s}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {query && results.length === 0 && (
          <EmptyState
            icon={Search}
            title="No results found"
            description={`No results matching "${query}"`}
          />
        )}

        {results.length > 0 && (
          <div className="max-w-2xl mx-auto space-y-2">
            <p className="text-sm text-muted-foreground">{results.length} results for &ldquo;{query}&rdquo;</p>
            {results.map((result, i) => {
              const config = typeConfig[result.type] || typeConfig.knowledge;
              const Icon = config.icon;
              return (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                >
                  <a href={result.url}>
                    <Card className="hover:shadow-md transition-shadow group">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                            <Icon className={`h-4 w-4 ${config.color}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">{result.title}</span>
                              <Badge variant="outline" className="text-[10px]">{result.type}</Badge>
                            </div>
                            <p className="text-xs text-muted-foreground mt-0.5">{result.description}</p>
                          </div>
                          <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                        </div>
                      </CardContent>
                    </Card>
                  </a>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
