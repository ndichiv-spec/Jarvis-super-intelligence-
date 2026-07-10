"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusDot } from "@/components/shared/status-dot";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/empty-state";
import { Puzzle, Plus, Shield, RotateCcw, Download, MoreHorizontal } from "lucide-react";
import { motion } from "framer-motion";

const extensions = [
  { id: "1", name: "AI Providers", description: "Registers AI provider connectors for model access", publisher: "JARVIS Core", version: "1.0.0", type: "AI Provider", status: "active" as const, permissions: ["command_registration"], hasUpdate: false },
  { id: "2", name: "Knowledge Connector", description: "Connects to external knowledge sources", publisher: "JARVIS Core", version: "1.0.0", type: "Knowledge", status: "active" as const, permissions: ["knowledge_access"], hasUpdate: false },
  { id: "3", name: "Tool Pack", description: "Registers collections of tools", publisher: "JARVIS Core", version: "0.9.5", type: "Tool Pack", status: "updatable" as const, permissions: ["tool_registration", "workspace_access"], hasUpdate: true },
  { id: "4", name: "Automation Pack", description: "Provides workflow templates and automation patterns", publisher: "JARVIS Core", version: "1.0.0", type: "Automation", status: "active" as const, permissions: ["workflow_registration"], hasUpdate: false, dependencies: ["Tool Pack"] },
  { id: "5", name: "UI Module", description: "Provides user interface components", publisher: "JARVIS Core", version: "1.0.0", type: "UI", status: "active" as const, permissions: [], hasUpdate: false },
  { id: "6", name: "Voice Extension", description: "Adds voice input and output capabilities", publisher: "JARVIS Core", version: "0.8.0", type: "Voice", status: "installed" as const, permissions: [], hasUpdate: true },
  { id: "7", name: "Vision Extension", description: "Adds image and video processing capabilities", publisher: "JARVIS Core", version: "1.0.0", type: "Vision", status: "active" as const, permissions: [], hasUpdate: false },
  { id: "8", name: "Enterprise Integration", description: "Provides enterprise system integration connectors", publisher: "JARVIS Core", version: "1.0.0", type: "Enterprise", status: "active" as const, permissions: ["command_registration"], hasUpdate: false },
  { id: "9", name: "Custom Connector", description: "Third-party API integration bridge", publisher: "Community", version: "2.1.0", type: "Integration", status: "disabled" as const, permissions: ["tool_registration", "event_subscription"], hasUpdate: false },
];

const statusColors: Record<string, string> = {
  active: "bg-status-success/10 text-status-success border-status-success/20",
  installed: "bg-status-info/10 text-status-info border-status-info/20",
  disabled: "bg-muted text-muted-foreground",
  error: "bg-status-error/10 text-status-error border-status-error/20",
  updatable: "bg-status-warning/10 text-status-warning border-status-warning/20",
};

export default function ExtensionsPage() {
  const [tab, setTab] = useState("all");

  const filtered = tab === "all" ? extensions : extensions.filter((e) => e.status === tab);

  return (
    <div className="pb-8">
      <PageHeader
        title="Extension Center"
        description="Manage your installed extensions and plugins"
        actions={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Browse Extensions
          </Button>
        }
      />

      <div className="px-6 space-y-4">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="all">All ({extensions.length})</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="installed">Installed</TabsTrigger>
            <TabsTrigger value="updatable">Updates Available</TabsTrigger>
            <TabsTrigger value="disabled">Disabled</TabsTrigger>
          </TabsList>

          <TabsContent value={tab} className="mt-4">
            {filtered.length === 0 ? (
              <EmptyState icon={Puzzle} title="No extensions found" />
            ) : (
              <div className="grid gap-3">
                {filtered.map((ext, i) => (
                  <motion.div
                    key={ext.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                  >
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 shrink-0">
                            <Puzzle className="h-5 w-5 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <CardTitle className="text-sm">{ext.name}</CardTitle>
                              <Badge variant="outline" className={statusColors[ext.status]}>
                                <StatusDot status={ext.status === "active" ? "success" : ext.status === "installed" ? "pending" : ext.status === "updatable" ? "warning" : ext.status === "disabled" ? "inactive" : "error"} className="mr-1" />
                                {ext.status === "updatable" ? "Update Available" : ext.status}
                              </Badge>
                            </div>
                            <CardDescription className="text-xs mt-0.5">{ext.description}</CardDescription>
                            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                              <span>v{ext.version}</span>
                              <span>by {ext.publisher}</span>
                              <Badge variant="secondary" className="text-[10px]">{ext.type}</Badge>
                            </div>
                            {ext.permissions.length > 0 && (
                              <div className="flex items-center gap-1 mt-1">
                                <Shield className="h-3 w-3 text-muted-foreground" />
                                {ext.permissions.map((p) => (
                                  <Badge key={p} variant="outline" className="text-[10px]">{p}</Badge>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            {ext.hasUpdate && (
                              <Button variant="default" size="sm">
                                <Download className="mr-1 h-3 w-3" />
                                Update
                              </Button>
                            )}
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
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
