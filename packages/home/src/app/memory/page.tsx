"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/empty-state";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Brain,
  Search,
  Archive,
  Trash2,
  Info,
  Star,
  Clock,
  Tag,
} from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { motion } from "framer-motion";

const memories = [
  { id: "1", content: "User prefers dark mode for all interfaces", type: "preference" as const, source: "Settings", confidence: 0.98, createdAt: new Date(Date.now() - 3600000), archived: false },
  { id: "2", content: "Working on Q2 financial analysis project", type: "context" as const, source: "Workspace", confidence: 0.92, createdAt: new Date(Date.now() - 7200000), archived: false },
  { id: "3", content: "Alex is the primary user account", type: "fact" as const, source: "Profile", confidence: 0.99, createdAt: new Date(Date.now() - 86400000), archived: false },
  { id: "4", content: "Frequently uses Python and TypeScript for development", type: "preference" as const, source: "Workspace", confidence: 0.85, createdAt: new Date(Date.now() - 172800000), archived: false },
  { id: "5", content: "Integration between Project Alpha and Knowledge Base", type: "relationship" as const, source: "Memory Engine", confidence: 0.78, createdAt: new Date(Date.now() - 259200000), archived: false },
  { id: "6", content: "Old project preference for Java", type: "preference" as const, source: "Workspace", confidence: 0.45, createdAt: new Date(Date.now() - 604800000), archived: true },
];

const typeColors: Record<string, string> = {
  fact: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  preference: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  context: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  relationship: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
};

export default function MemoryPage() {
  const [search, setSearch] = useState("");
  const [showArchived, setShowArchived] = useState(false);
  const [tab, setTab] = useState("all");

  const filtered = memories.filter((m) => {
    if (tab === "active" && m.archived) return false;
    if (tab === "archived" && !m.archived) return false;
    if (search && !m.content.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="pb-8">
      <PageHeader
        title="Memory Center"
        description="View and manage what JARVIS remembers"
        actions={
          <Button variant="outline" size="sm">
            <Info className="mr-2 h-4 w-4" />
            How Memory Works
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search memories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="all">All Memories</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="archived">Archived</TabsTrigger>
          </TabsList>

          <TabsContent value={tab} className="mt-4">
            {filtered.length === 0 ? (
              <EmptyState
                icon={Brain}
                title="No memories found"
                description={search ? "Try a different search term" : "Memories will appear as you interact with JARVIS"}
              />
            ) : (
              <div className="space-y-3">
                {filtered.map((memory, i) => (
                  <motion.div
                    key={memory.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <Card className={`${memory.archived ? "opacity-60" : ""}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="secondary" className={typeColors[memory.type]}>
                                {memory.type}
                              </Badge>
                              <Badge variant="outline" className="text-[10px]">
                                {Math.round(memory.confidence * 100)}% confidence
                              </Badge>
                              {memory.archived && (
                                <Badge variant="outline" className="text-[10px]">
                                  Archived
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm">{memory.content}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Tag className="h-3 w-3" />
                                {memory.source}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {formatRelativeTime(memory.createdAt)}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              {memory.archived ? <Star className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
                            </Button>
                            <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
