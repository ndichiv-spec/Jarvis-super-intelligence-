"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { EmptyState } from "@/components/shared/empty-state";
import { Plus, FolderKanban, Search, ArrowUpRight, Clock } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import { motion } from "framer-motion";

const projects = [
  { id: "1", name: "Market Analysis Q2", description: "Comprehensive analysis of Q2 market trends and competitor movements", status: "active" as const, progress: 75, milestones: 5, conversations: 12, updatedAt: new Date(Date.now() - 3600000) },
  { id: "2", name: "Auth System Overhaul", description: "Complete redesign of authentication system with OAuth 2.0 support", status: "active" as const, progress: 45, milestones: 8, conversations: 24, updatedAt: new Date(Date.now() - 7200000) },
  { id: "3", name: "Documentation Refresh", description: "Update all public documentation for v2.0 release", status: "paused" as const, progress: 30, milestones: 3, conversations: 7, updatedAt: new Date(Date.now() - 86400000) },
  { id: "4", name: "Performance Optimization", description: "Identify and resolve performance bottlenecks across the platform", status: "completed" as const, progress: 100, milestones: 4, conversations: 18, updatedAt: new Date(Date.now() - 172800000) },
];

const statusColors: Record<string, string> = {
  active: "bg-status-success/10 text-status-success border-status-success/20",
  completed: "bg-status-info/10 text-status-info border-status-info/20",
  paused: "bg-status-warning/10 text-status-warning border-status-warning/20",
  archived: "bg-muted text-muted-foreground",
};

export default function ProjectsPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  const filtered = projects.filter((p) => {
    if (filter !== "all" && p.status !== filter) return false;
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="pb-8">
      <PageHeader
        title="Projects"
        description="Manage your projects and track progress"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </Button>
        }
      />

      <div className="px-6 mb-6 flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {filtered.length === 0 ? (
        <div className="px-6">
          <EmptyState
            icon={FolderKanban}
            title="No projects found"
            description={search ? "Try a different search term" : "Create your first project to get started"}
            action={!search && <Button><Plus className="mr-2 h-4 w-4" />New Project</Button>}
          />
        </div>
      ) : (
        <div className="px-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((project, i) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="h-full hover:shadow-md transition-shadow cursor-pointer group">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{project.name}</CardTitle>
                      <CardDescription className="mt-1">{project.description}</CardDescription>
                    </div>
                    <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className={statusColors[project.status]}>
                      {project.status}
                    </Badge>
                    <span className="text-sm font-medium">{project.progress}%</span>
                  </div>
                  <Progress value={project.progress} />
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{project.milestones} milestones</span>
                    <span>{project.conversations} conversations</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatRelativeTime(project.updatedAt)}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
