"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";
import { Box, Building2, FolderKanban, Users, CheckCircle2, Clock, AlertTriangle } from "lucide-react";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

interface Organization {
  id: string;
  name: string;
  slug: string;
  memberCount: number;
}

interface Project {
  id: string;
  name: string;
  status: "active" | "inactive" | "pending";
  progress: number;
  updatedAt: string;
}

const mockOrganizations: Organization[] = [
  { id: "1", name: "JARVIS AI", slug: "jarvis-ai", memberCount: 24 },
  { id: "2", name: "Research Lab", slug: "research-lab", memberCount: 12 },
  { id: "3", name: "Platform Engineering", slug: "platform-eng", memberCount: 18 },
  { id: "4", name: "Data Science Hub", slug: "ds-hub", memberCount: 9 },
  { id: "5", name: "DevOps Center", slug: "devops-center", memberCount: 15 },
];

const mockProjects: Project[] = [
  { id: "1", name: "Agent Runtime Core", status: "active", progress: 78, updatedAt: "2 hours ago" },
  { id: "2", name: "Knowledge Indexer", status: "active", progress: 45, updatedAt: "5 hours ago" },
  { id: "3", name: "Tool Gateway SDK", status: "pending", progress: 15, updatedAt: "1 day ago" },
  { id: "4", name: "Memory Store Optimization", status: "active", progress: 92, updatedAt: "3 hours ago" },
  { id: "5", name: "Security Audit Pipeline", status: "inactive", progress: 100, updatedAt: "1 week ago" },
  { id: "6", name: "Workflow Orchestrator", status: "active", progress: 63, updatedAt: "4 hours ago" },
];

const environments = [
  { name: "Development", status: "active" as const, url: "dev.jarvis.ai", version: "2.4.0-dev" },
  { name: "Staging", status: "degraded" as const, url: "staging.jarvis.ai", version: "2.3.1-rc" },
  { name: "Production", status: "healthy" as const, url: "jarvis.ai", version: "2.3.0" },
];

const projectStatusConfig: Record<string, { label: string; icon: typeof CheckCircle2; color: string; dotStatus: "active" | "inactive" | "pending" }> = {
  active: { label: "Active", icon: CheckCircle2, color: "text-status-success", dotStatus: "active" },
  inactive: { label: "Inactive", icon: AlertTriangle, color: "text-muted-foreground", dotStatus: "inactive" },
  pending: { label: "Pending", icon: Clock, color: "text-status-warning", dotStatus: "pending" },
};

const organizationColumns: Column<Organization>[] = [
  { key: "name", header: "Name", cell: (org) => <span className="font-medium">{org.name}</span> },
  { key: "slug", header: "Slug", cell: (org) => <code className="text-xs text-muted-foreground">{org.slug}</code> },
  {
    key: "memberCount", header: "Members", className: "text-right",
    cell: (org) => <span className="text-muted-foreground">{org.memberCount}</span>,
  },
];

const projectColumns: Column<Project>[] = [
  { key: "name", header: "Name", cell: (p) => <span className="font-medium">{p.name}</span> },
  {
    key: "status", header: "Status",
    cell: (p) => {
      const cfg = projectStatusConfig[p.status];
      return (
        <div className="flex items-center gap-1.5">
          <StatusDot status={cfg.dotStatus} />
          <span className="text-xs text-muted-foreground">{cfg.label}</span>
        </div>
      );
    },
  },
  {
    key: "progress", header: "Progress",
    cell: (p) => (
      <div className="flex items-center gap-2 w-32">
        <Progress value={p.progress} className="h-1.5" />
        <span className="text-xs text-muted-foreground w-8 text-right">{p.progress}%</span>
      </div>
    ),
  },
  { key: "updatedAt", header: "Updated", cell: (p) => <span className="text-xs text-muted-foreground">{p.updatedAt}</span> },
];

function cn(...classes: (string | false | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export default function WorkspacePage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="pb-8">
      <PageHeader
        title="Workspace Manager"
        description="Manage workspaces, organizations, projects, and environments"
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="flex items-center gap-3">
          <Select defaultValue="main">
            <SelectTrigger className="w-56">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="main">Main Workspace</SelectItem>
              <SelectItem value="sandbox">Sandbox</SelectItem>
              <SelectItem value="enterprise">Enterprise</SelectItem>
            </SelectContent>
          </Select>
          <Badge variant="secondary" className="gap-1.5 text-xs">
            <StatusDot status="active" />
            Production
          </Badge>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <motion.div variants={itemVariants}>
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="projects">Projects</TabsTrigger>
            </TabsList>
          </motion.div>

          <TabsContent value="overview" className="space-y-6 mt-4">
            <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard title="Workspaces" value={3} icon={Box} trend={{ value: 1, positive: true }} />
              <StatCard title="Organizations" value={mockOrganizations.length} icon={Building2} />
              <StatCard title="Active Projects" value={mockProjects.filter((p) => p.status === "active").length} icon={FolderKanban} trend={{ value: 2, positive: true }} />
              <StatCard title="Members" value={78} icon={Users} trend={{ value: 5, positive: true }} />
            </motion.div>

            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Organizations</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable columns={organizationColumns} data={mockOrganizations} />
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={itemVariants}>
              <SectionHeader title="Environment Metadata" description="Deployment environments and current status" className="mb-3" />
              <div className="grid gap-3 sm:grid-cols-3">
                {environments.map((env) => (
                  <Card key={env.name}>
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{env.name}</span>
                        <Badge variant="outline" className="gap-1 text-xs">
                          <StatusDot status={env.status} />
                          <span className="capitalize">{env.status}</span>
                        </Badge>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs text-muted-foreground">
                          <span className="font-medium text-foreground">URL:</span> {env.url}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          <span className="font-medium text-foreground">Version:</span> {env.version}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </motion.div>
          </TabsContent>

          <TabsContent value="projects" className="space-y-4 mt-4">
            <motion.div variants={itemVariants}>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">All Projects</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <DataTable columns={projectColumns} data={mockProjects} />
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
}
