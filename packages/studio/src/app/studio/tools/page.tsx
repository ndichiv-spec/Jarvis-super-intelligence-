"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { DataTable, type Column } from "@/components/shared/data-table";
import { StatusDot } from "@/components/shared/status-dot";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import * as React from "react";
import { Wrench, Shield, Clock, Activity, CheckCircle2, XCircle, FolderOpen, Globe, Database, Mail, Image, FileText, Terminal } from "lucide-react";
import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
  status: "active" | "disabled" | "error";
  executionCount: number;
  lastUsed: string;
}

interface Execution {
  id: string;
  toolId: string;
  toolName: string;
  status: "success" | "failure";
  duration: string;
  timestamp: string;
}

interface PermissionGroup {
  toolId: string;
  toolName: string;
  permissions: string[];
}

const tools: Tool[] = [
  { id: "1", name: "FileReader", description: "Read and parse files from the local filesystem", category: "I/O", status: "active", executionCount: 1423, lastUsed: "2 min ago" },
  { id: "2", name: "WebScraper", description: "Extract content and metadata from web pages", category: "Network", status: "active", executionCount: 876, lastUsed: "15 min ago" },
  { id: "3", name: "DatabaseQuery", description: "Execute SQL queries against connected databases", category: "Data", status: "active", executionCount: 2456, lastUsed: "1 min ago" },
  { id: "4", name: "EmailSender", description: "Send emails via configured SMTP providers", category: "Communication", status: "active", executionCount: 534, lastUsed: "1 hour ago" },
  { id: "5", name: "ImageProcessor", description: "Resize, crop, filter, and analyze images", category: "Media", status: "disabled", executionCount: 321, lastUsed: "3 days ago" },
  { id: "6", name: "TextAnalyzer", description: "Perform NLP tasks including sentiment and entity extraction", category: "AI/ML", status: "active", executionCount: 1890, lastUsed: "5 min ago" },
  { id: "7", name: "APIClient", description: "Make HTTP requests to external REST and GraphQL APIs", category: "Network", status: "active", executionCount: 3102, lastUsed: "30 sec ago" },
  { id: "8", name: "DataTransformer", description: "Transform data between JSON, CSV, XML, and YAML formats", category: "Data", status: "error", executionCount: 678, lastUsed: "45 min ago" },
];

const executions: Execution[] = [
  { id: "e1", toolId: "APIClient", toolName: "APIClient", status: "success", duration: "234ms", timestamp: "2026-06-30 17:45:12" },
  { id: "e2", toolId: "DatabaseQuery", toolName: "DatabaseQuery", status: "success", duration: "1.2s", timestamp: "2026-06-30 17:44:58" },
  { id: "e3", toolId: "FileReader", toolName: "FileReader", status: "success", duration: "87ms", timestamp: "2026-06-30 17:43:21" },
  { id: "e4", toolId: "APIClient", toolName: "APIClient", status: "failure", duration: "5.1s", timestamp: "2026-06-30 17:42:05" },
  { id: "e5", toolId: "TextAnalyzer", toolName: "TextAnalyzer", status: "success", duration: "1.8s", timestamp: "2026-06-30 17:41:33" },
  { id: "e6", toolId: "WebScraper", toolName: "WebScraper", status: "success", duration: "3.4s", timestamp: "2026-06-30 17:40:00" },
  { id: "e7", toolId: "DataTransformer", toolName: "DataTransformer", status: "failure", duration: "456ms", timestamp: "2026-06-30 17:38:44" },
  { id: "e8", toolId: "EmailSender", toolName: "EmailSender", status: "success", duration: "1.1s", timestamp: "2026-06-30 17:36:12" },
  { id: "e9", toolId: "ImageProcessor", toolName: "ImageProcessor", status: "failure", duration: "12.3s", timestamp: "2026-06-30 17:30:00" },
  { id: "e10", toolId: "DatabaseQuery", toolName: "DatabaseQuery", status: "success", duration: "890ms", timestamp: "2026-06-30 17:25:18" },
];

const permissionGroups: PermissionGroup[] = [
  {
    toolId: "FileReader",
    toolName: "FileReader",
    permissions: ["filesystem.read", "filesystem.read.recursive", "filesystem.metadata"],
  },
  {
    toolId: "WebScraper",
    toolName: "WebScraper",
    permissions: ["network.http", "network.dns", "storage.cache"],
  },
  {
    toolId: "DatabaseQuery",
    toolName: "DatabaseQuery",
    permissions: ["database.read", "database.write", "connection.manage"],
  },
  {
    toolId: "EmailSender",
    toolName: "EmailSender",
    permissions: ["smtp.send", "identity.read", "template.read"],
  },
  {
    toolId: "ImageProcessor",
    toolName: "ImageProcessor",
    permissions: ["filesystem.read", "filesystem.write", "memory.process"],
  },
  {
    toolId: "TextAnalyzer",
    toolName: "TextAnalyzer",
    permissions: ["ai.inference", "model.load", "memory.analyze"],
  },
  {
    toolId: "APIClient",
    toolName: "APIClient",
    permissions: ["network.http", "network.https", "auth.token", "auth.refresh"],
  },
  {
    toolId: "DataTransformer",
    toolName: "DataTransformer",
    permissions: ["filesystem.read", "filesystem.write", "memory.transform"],
  },
];

const categoryIcons: Record<string, React.ElementType> = {
  "I/O": FolderOpen,
  "Network": Globe,
  "Data": Database,
  "Communication": Mail,
  "Media": Image,
  "AI/ML": Terminal,
};

function getCategoryIcon(category: string) {
  return categoryIcons[category] || Terminal;
}

const toolColumns: Column<Tool>[] = [
  {
    key: "name",
    header: "Name",
    cell: (tool) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/10">
          {React.createElement(getCategoryIcon(tool.category), { className: "h-3.5 w-3.5 text-primary" })}
        </div>
        <span className="font-medium">{tool.name}</span>
      </div>
    ),
  },
  { key: "description", header: "Description", cell: (tool) => <span className="text-muted-foreground">{tool.description}</span> },
  {
    key: "category",
    header: "Category",
    cell: (tool) => <Badge variant="outline" className="text-xs">{tool.category}</Badge>,
  },
  {
    key: "status",
    header: "Status",
    cell: (tool) => (
      <div className="flex items-center gap-1.5">
        <StatusDot status={tool.status} />
        <span className="text-xs capitalize">{tool.status}</span>
      </div>
    ),
  },
  {
    key: "executionCount",
    header: "Executions",
    cell: (tool) => <span className="font-mono text-xs">{tool.executionCount.toLocaleString()}</span>,
  },
  { key: "lastUsed", header: "Last Used", cell: (tool) => <span className="text-muted-foreground text-xs">{tool.lastUsed}</span> },
];

const executionColumns: Column<Execution>[] = [
  { key: "toolId", header: "Tool", cell: (exec) => <span className="font-medium">{exec.toolName}</span> },
  {
    key: "status",
    header: "Status",
    cell: (exec) => (
      <div className="flex items-center gap-1.5">
        {exec.status === "success" ? (
          <CheckCircle2 className="h-3.5 w-3.5 text-status-success" />
        ) : (
          <XCircle className="h-3.5 w-3.5 text-status-error" />
        )}
        <span className={exec.status === "success" ? "text-status-success" : "text-status-error"}>
          {exec.status}
        </span>
      </div>
    ),
  },
  { key: "duration", header: "Duration", cell: (exec) => <span className="font-mono text-xs">{exec.duration}</span> },
  { key: "timestamp", header: "Timestamp", cell: (exec) => <span className="text-muted-foreground text-xs">{exec.timestamp}</span> },
];

export default function ToolManagerPage() {
  const { data: toolsData, loading, error } = useData(() => api.tools.list());
  const toolList = (toolsData || tools) as Tool[];
  const activeCount = toolList.filter((t) => t.status === "active").length;
  const disabledCount = toolList.filter((t) => t.status === "disabled").length;
  const totalExecutions = toolList.reduce((sum, t) => sum + t.executionCount, 0);
  return (
    <div className="pb-8">
      <PageHeader
        title="Tool Manager"
        description="Manage tool definitions, permissions, and execution history"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Tools" value={tools.length} icon={Wrench} />
          <StatCard title="Active" value={activeCount} icon={Activity} trend={{ value: Math.round((activeCount / tools.length) * 100), positive: true }} />
          <StatCard title="Disabled" value={disabledCount} icon={Shield} />
          <StatCard title="Total Executions" value={totalExecutions.toLocaleString()} icon={Clock} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card>
            <CardContent className="p-0">
              <Tabs defaultValue="installed" className="w-full">
                <div className="border-b border-studio-border px-4 pt-3">
                  <TabsList>
                    <TabsTrigger value="installed" className="gap-1.5">
                      <Wrench className="h-3.5 w-3.5" />
                      Installed Tools
                    </TabsTrigger>
                    <TabsTrigger value="permissions" className="gap-1.5">
                      <Shield className="h-3.5 w-3.5" />
                      Permissions
                    </TabsTrigger>
                    <TabsTrigger value="history" className="gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      Execution History
                    </TabsTrigger>
                  </TabsList>
                </div>

                <TabsContent value="installed" className="m-0">
                  <DataTable columns={toolColumns} data={toolList} emptyMessage="No tools installed" />
                </TabsContent>

                <TabsContent value="permissions" className="m-0 p-4">
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {permissionGroups.map((group) => (
                      <Card key={group.toolId}>
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <Shield className="h-3.5 w-3.5 text-primary" />
                            {group.toolName}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-1">
                            {group.permissions.map((perm) => (
                              <div key={perm} className="flex items-center gap-2 rounded-md bg-muted/50 px-2 py-1">
                                <CheckCircle2 className="h-3 w-3 text-status-success shrink-0" />
                                <code className="text-xs font-mono">{perm}</code>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="history" className="m-0">
                  <DataTable columns={executionColumns} data={executions} emptyMessage="No execution history" />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}

