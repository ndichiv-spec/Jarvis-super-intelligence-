"use client";

import { useState } from "react";
import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Brain, Archive, Tag, Trash2, Layers } from "lucide-react";
import { motion } from "framer-motion";
import { formatRelativeTime } from "@/lib/utils";

type MemoryType = "fact" | "preference" | "context" | "relationship";
type PolicyType = "retention" | "archival" | "deletion";

interface MemoryItem {
  id: string;
  content: string;
  type: MemoryType;
  source: string;
  confidence: number;
  reasoning: string;
  createdAt: Date;
  archived: boolean;
}

interface MemoryCategory {
  type: MemoryType;
  count: number;
}

interface MemoryPolicy {
  id: string;
  name: string;
  type: PolicyType;
  enabled: boolean;
  retentionDays?: number;
}

const memoryItems: MemoryItem[] = [
  { id: "m1", content: "User prefers dark mode across all applications", type: "preference", source: "conversation", confidence: 92, reasoning: "Explicitly stated in chat history", createdAt: new Date("2026-06-25"), archived: false },
  { id: "m2", content: "JARVIS was initialized on June 1st 2026", type: "fact", source: "system", confidence: 100, reasoning: "System timestamp recorded at bootstrap", createdAt: new Date("2026-06-01"), archived: false },
  { id: "m3", content: "Active project: building a code analysis tool", type: "context", source: "workspace", confidence: 85, reasoning: "Current workspace session context", createdAt: new Date("2026-06-28"), archived: false },
  { id: "m4", content: "User is a senior software engineer focused on AI", type: "fact", source: "profile", confidence: 95, reasoning: "Extracted from user profile data", createdAt: new Date("2026-06-10"), archived: false },
  { id: "m5", content: "User prefers concise responses with code examples", type: "preference", source: "conversation", confidence: 78, reasoning: "Inferred from response feedback patterns", createdAt: new Date("2026-06-22"), archived: false },
  { id: "m6", content: "Knowledge base connector uses Qdrant vector store", type: "relationship", source: "system", confidence: 98, reasoning: "Defined in integration configuration", createdAt: new Date("2026-06-15"), archived: false },
  { id: "m7", content: "User's timezone is UTC+8", type: "fact", source: "profile", confidence: 90, reasoning: "Extracted from account settings", createdAt: new Date("2026-06-05"), archived: true },
  { id: "m8", content: "Memory consolidation runs every 6 hours", type: "context", source: "system", confidence: 100, reasoning: "System scheduled task configuration", createdAt: new Date("2026-06-20"), archived: false },
  { id: "m9", content: "LangGraph workflows depend on memory module", type: "relationship", source: "analysis", confidence: 72, reasoning: "Inferred from dependency graph traversal", createdAt: new Date("2026-06-27"), archived: false },
  { id: "m10", content: "User has disabled telemetry collection", type: "preference", source: "settings", confidence: 96, reasoning: "Explicit toggle in privacy settings", createdAt: new Date("2026-06-18"), archived: true },
  { id: "m11", content: "Agent timeout is set to 60 seconds", type: "fact", source: "configuration", confidence: 100, reasoning: "Hardcoded in agent configuration manifest", createdAt: new Date("2026-06-12"), archived: false },
  { id: "m12", content: "Memory inspector has sub-100ms query latency", type: "context", source: "monitoring", confidence: 65, reasoning: "Averaged from last 100 query samples", createdAt: new Date("2026-06-29"), archived: false },
];

const memoryPolicies: MemoryPolicy[] = [
  { id: "p1", name: "Default Retention", type: "retention", enabled: true, retentionDays: 90 },
  { id: "p2", name: "Auto-Archive Inactive", type: "archival", enabled: true },
  { id: "p3", name: "Deprecated Fact Cleanup", type: "deletion", enabled: false },
];

const activeItems = memoryItems.filter((m) => !m.archived);
const archivedItems = memoryItems.filter((m) => m.archived);

const categories: MemoryCategory[] = [
  { type: "fact", count: memoryItems.filter((m) => m.type === "fact").length },
  { type: "preference", count: memoryItems.filter((m) => m.type === "preference").length },
  { type: "context", count: memoryItems.filter((m) => m.type === "context").length },
  { type: "relationship", count: memoryItems.filter((m) => m.type === "relationship").length },
];

const typeColors: Record<string, "info" | "success" | "warning" | "default"> = {
  fact: "info",
  preference: "success",
  context: "warning",
  relationship: "default",
};

const policyTypeColors: Record<string, "info" | "warning" | "destructive"> = {
  retention: "info",
  archival: "warning",
  deletion: "destructive",
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const memoryColumns: Column<MemoryItem>[] = [
  { key: "content", header: "Content", cell: (m) => <span className="font-medium max-w-[240px] truncate block">{m.content}</span> },
  {
    key: "type", header: "Type", cell: (m) => (
      <Badge variant={typeColors[m.type]} className="capitalize">{m.type}</Badge>
    ),
  },
  { key: "source", header: "Source", cell: (m) => <span className="text-muted-foreground capitalize">{m.source}</span> },
  {
    key: "confidence", header: "Confidence", cell: (m) => (
      <div className="flex items-center gap-2 min-w-[100px]">
        <Progress value={m.confidence} className="h-1.5" />
        <span className="text-xs text-muted-foreground w-8 text-right">{m.confidence}%</span>
      </div>
    ),
  },
  { key: "reasoning", header: "Reasoning", cell: (m) => <span className="text-muted-foreground text-xs max-w-[180px] truncate block">{m.reasoning}</span> },
  { key: "createdAt", header: "Created", cell: (m) => <span className="text-muted-foreground text-xs">{formatRelativeTime(m.createdAt)}</span> },
  {
    key: "archived", header: "Status", cell: (m) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={m.archived ? "archived" : "active"} />
        <span className="text-xs text-muted-foreground capitalize">{m.archived ? "archived" : "active"}</span>
      </div>
    ),
  },
];

const policyColumns: Column<MemoryPolicy>[] = [
  { key: "name", header: "Name", cell: (p) => <span className="font-medium">{p.name}</span> },
  {
    key: "type", header: "Type", cell: (p) => (
      <Badge variant={policyTypeColors[p.type]} className="capitalize">{p.type}</Badge>
    ),
  },
  {
    key: "enabled", header: "Enabled", cell: (p) => (
      <Switch checked={p.enabled} onCheckedChange={() => {}} />
    ),
  },
  { key: "retentionDays", header: "Retention (days)", cell: (p) => <span className="text-muted-foreground">{p.retentionDays ?? "—"}</span> },
];

const archivedColumns: Column<MemoryItem>[] = [
  { key: "content", header: "Content", cell: (m) => <span className="font-medium max-w-[240px] truncate block">{m.content}</span> },
  {
    key: "type", header: "Type", cell: (m) => (
      <Badge variant={typeColors[m.type]} className="capitalize">{m.type}</Badge>
    ),
  },
  { key: "source", header: "Source", cell: (m) => <span className="text-muted-foreground capitalize">{m.source}</span> },
  {
    key: "confidence", header: "Confidence", cell: (m) => (
      <div className="flex items-center gap-2 min-w-[100px]">
        <Progress value={m.confidence} className="h-1.5" />
        <span className="text-xs text-muted-foreground w-8 text-right">{m.confidence}%</span>
      </div>
    ),
  },
  { key: "createdAt", header: "Archived", cell: (m) => <span className="text-muted-foreground text-xs">{formatRelativeTime(m.createdAt)}</span> },
  {
    key: "actions", header: "Actions", cell: (m) => (
      <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-destructive">
        <Trash2 className="h-4 w-4" />
      </Button>
    ),
  },
];

export default function MemoryInspectorPage() {
  const [activeTab, setActiveTab] = useState("timeline");
  const { data: memData } = useData(() => api.memory.list());
  const { data: polData } = useData(() => api.memory.policies());
  const memoryItemsList = (memData || memoryItems) as MemoryItem[];
  const memoryPoliciesList = (polData || memoryPolicies) as MemoryPolicy[];
  const activeItems = memoryItemsList.filter((m) => !m.archived);
  const archivedItems = memoryItemsList.filter((m) => m.archived);
  const categories: MemoryCategory[] = [
    { type: "fact", count: memoryItemsList.filter((m) => m.type === "fact").length },
    { type: "preference", count: memoryItemsList.filter((m) => m.type === "preference").length },
    { type: "context", count: memoryItemsList.filter((m) => m.type === "context").length },
    { type: "relationship", count: memoryItemsList.filter((m) => m.type === "relationship").length },
  ];

  return (
    <div className="pb-8">
      <PageHeader
        title="Memory Inspector"
        description="Transparent view into the Memory Platform"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Memories" value={memoryItemsList.length} icon={Brain} />
          <StatCard title="Active" value={activeItems.length} icon={Layers} />
          <StatCard title="Archived" value={archivedItems.length} icon={Archive} />
          <StatCard title="Categories" value={categories.length} icon={Tag} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardContent className="p-0">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <div className="border-b px-4 py-2">
                  <TabsList>
                    <TabsTrigger value="timeline" className="gap-1.5">
                      <Layers className="h-4 w-4" />
                      Memory Timeline
                    </TabsTrigger>
                    <TabsTrigger value="categories" className="gap-1.5">
                      <Tag className="h-4 w-4" />
                      Categories
                    </TabsTrigger>
                    <TabsTrigger value="policies" className="gap-1.5">
                      <Archive className="h-4 w-4" />
                      Policies
                    </TabsTrigger>
                    <TabsTrigger value="archived" className="gap-1.5">
                      <Archive className="h-4 w-4" />
                      Archived
                    </TabsTrigger>
                  </TabsList>
                </div>

                <TabsContent value="timeline" className="m-0">
                  <DataTable columns={memoryColumns} data={memoryItemsList} />
                </TabsContent>

                <TabsContent value="categories" className="m-0 p-4">
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    {categories.map((cat) => (
                      <Card key={cat.type} className="hover:bg-studio-hover transition-colors">
                        <CardContent className="p-4 flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Tag className="h-5 w-5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium capitalize">{cat.type}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className="text-2xl font-semibold">{cat.count}</span>
                              <Badge variant={typeColors[cat.type]} className="text-[10px] capitalize">{cat.type}</Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="policies" className="m-0">
                  <DataTable columns={policyColumns} data={memoryPoliciesList} />
                </TabsContent>

                <TabsContent value="archived" className="m-0">
                  <DataTable columns={archivedColumns} data={archivedItems} />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
