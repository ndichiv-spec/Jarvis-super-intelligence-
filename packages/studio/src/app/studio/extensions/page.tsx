"use client";

import { useData } from "@/lib/use-data";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusDot } from "@/components/shared/status-dot";
import { DataTable } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { type Column } from "@/components/shared/data-table";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Puzzle, Download, RefreshCw, Package,
  Store, CheckCircle, XCircle, AlertTriangle,
  ArrowUp, Eye,
} from "lucide-react";
import { motion } from "framer-motion";

type ExtensionStatus = "installed" | "active" | "disabled" | "error";

interface Extension {
  id: string;
  name: string;
  description: string;
  publisher: string;
  version: string;
  status: ExtensionStatus;
  permissions: string[];
  installedAt: string;
}

interface UpdatableExtension {
  id: string;
  name: string;
  publisher: string;
  installedVersion: string;
  latestVersion: string;
  changelog: string;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const statusConfig: Record<ExtensionStatus, { label: string; variant: "success" | "info" | "secondary" | "destructive" }> = {
  active: { label: "Active", variant: "success" },
  installed: { label: "Installed", variant: "info" },
  disabled: { label: "Disabled", variant: "secondary" },
  error: { label: "Error", variant: "destructive" },
};

const extensions: Extension[] = [
  {
    id: "ext-1",
    name: "Vision Pro",
    description: "Advanced computer vision and image recognition capabilities",
    publisher: "JARVIS Labs",
    version: "2.1.0",
    status: "active",
    permissions: ["camera", "filesystem", "network"],
    installedAt: "2026-03-15",
  },
  {
    id: "ext-2",
    name: "Voice Pack",
    description: "Multi-language speech synthesis and voice command processing",
    publisher: "JARVIS Labs",
    version: "1.8.3",
    status: "active",
    permissions: ["microphone", "audio"],
    installedAt: "2026-02-28",
  },
  {
    id: "ext-3",
    name: "Analytics Plus",
    description: "Real-time analytics dashboard with custom metric tracking",
    publisher: "DataForge Inc.",
    version: "3.0.1",
    status: "disabled",
    permissions: ["storage", "network"],
    installedAt: "2026-01-10",
  },
  {
    id: "ext-4",
    name: "Security Suite",
    description: "Threat detection, vulnerability scanning, and compliance monitoring",
    publisher: "CyberShield",
    version: "1.2.0",
    status: "active",
    permissions: ["admin", "network", "filesystem", "process"],
    installedAt: "2026-04-01",
  },
  {
    id: "ext-5",
    name: "Data Connector",
    description: "Connect to external databases, APIs, and data warehouses",
    publisher: "DataForge Inc.",
    version: "2.5.0",
    status: "error",
    permissions: ["network", "storage"],
    installedAt: "2025-11-20",
  },
  {
    id: "ext-6",
    name: "Custom Dashboard",
    description: "Build and share custom dashboards with drag-and-drop widgets",
    publisher: "JARVIS Labs",
    version: "1.0.0",
    status: "installed",
    permissions: ["storage", "ui"],
    installedAt: "2026-05-12",
  },
];

const updatableExtensions: UpdatableExtension[] = [
  {
    id: "upd-1",
    name: "Vision Pro",
    publisher: "JARVIS Labs",
    installedVersion: "2.1.0",
    latestVersion: "2.2.0",
    changelog: "Improved OCR accuracy, new model variants, performance optimizations",
  },
  {
    id: "upd-2",
    name: "Voice Pack",
    publisher: "JARVIS Labs",
    installedVersion: "1.8.3",
    latestVersion: "1.9.0",
    changelog: "Added Italian and Korean voices, reduced latency by 30%",
  },
  {
    id: "upd-3",
    name: "Security Suite",
    publisher: "CyberShield",
    installedVersion: "1.2.0",
    latestVersion: "1.3.0",
    changelog: "New CVE feed integration, improved false-positive filtering",
  },
];

const installedColumns: Column<Extension>[] = [
  {
    key: "name",
    header: "Name",
    cell: (ext) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/10">
          <Package className="h-3.5 w-3.5 text-primary" />
        </div>
        <div>
          <p className="text-sm font-medium">{ext.name}</p>
          <p className="text-xs text-muted-foreground">{ext.publisher}</p>
        </div>
      </div>
    ),
  },
  {
    key: "description",
    header: "Description",
    cell: (ext) => <span className="text-xs text-muted-foreground">{ext.description}</span>,
    className: "hidden md:table-cell",
  },
  {
    key: "version",
    header: "Version",
    cell: (ext) => <Badge variant="outline" className="text-xs">{ext.version}</Badge>,
  },
  {
    key: "status",
    header: "Status",
    cell: (ext) => {
      const cfg = statusConfig[ext.status];
      return (
        <Badge variant={cfg.variant} className="gap-1 text-xs">
          <StatusDot status={ext.status as "healthy" | "degraded" | "critical" | "active" | "inactive" | "error" | "warning" | "success" | "pending" | "running" | "idle" | "busy" | "available" | "disabled" | "maintenance" | "draft" | "published" | "archived" | "suspended"} />
          {cfg.label}
        </Badge>
      );
    },
  },
  {
    key: "permissions",
    header: "Permissions",
    cell: (ext) => (
      <div className="flex flex-wrap gap-1">
        {ext.permissions.map((p) => (
          <Badge key={p} variant="secondary" className="text-[10px]">{p}</Badge>
        ))}
      </div>
    ),
    className: "hidden lg:table-cell",
  },
  {
    key: "installedAt",
    header: "Installed",
    cell: (ext) => <span className="text-xs text-muted-foreground">{ext.installedAt}</span>,
    className: "hidden xl:table-cell",
  },
];

const updatesColumns: Column<UpdatableExtension>[] = [
  {
    key: "name",
    header: "Name",
    cell: (upd) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-amber-500/10">
          <ArrowUp className="h-3.5 w-3.5 text-amber-500" />
        </div>
        <div>
          <p className="text-sm font-medium">{upd.name}</p>
          <p className="text-xs text-muted-foreground">{upd.publisher}</p>
        </div>
      </div>
    ),
  },
  {
    key: "versions",
    header: "Versions",
    cell: (upd) => (
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="text-xs">{upd.installedVersion}</Badge>
        <ArrowUp className="h-3 w-3 text-muted-foreground" />
        <Badge variant="success" className="text-xs">{upd.latestVersion}</Badge>
      </div>
    ),
  },
  {
    key: "changelog",
    header: "Changelog",
    cell: (upd) => <span className="text-xs text-muted-foreground">{upd.changelog}</span>,
    className: "hidden md:table-cell",
  },
  {
    key: "actions",
    header: "",
    cell: () => (
      <Button size="sm" className="h-7 text-xs gap-1">
        <RefreshCw className="h-3 w-3" /> Update
      </Button>
    ),
  },
];

export default function ExtensionsPage() {
  const { data: extData, loading, error } = useData(() => api.extensions.list());
  const extList = (extData || extensions) as Extension[];
  const updatableList = updatableExtensions;
  const stats = {
    total: extList.length,
    active: extList.filter((e) => e.status === "active").length,
    disabled: extList.filter((e) => e.status === "disabled").length,
    updates: updatableList.length,
  };
  return (
    <div className="pb-8">
      <PageHeader
        title="Extension Manager"
        description="Install, activate, update, and manage extensions"
        actions={
          <Button size="sm" className="gap-1.5">
            <Download className="h-4 w-4" /> Browse Extensions
          </Button>
        }
      />

      <motion.div variants={containerVariants} initial="hidden" animate="visible" className="px-6 space-y-6 mt-6">
        <motion.div variants={itemVariants} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Total Extensions" value={stats.total} icon={Puzzle} />
          <StatCard title="Active" value={stats.active} icon={CheckCircle} trend={{ value: 2, positive: true }} />
          <StatCard title="Disabled" value={stats.disabled} icon={XCircle} />
          <StatCard title="Updates Available" value={stats.updates} icon={RefreshCw} trend={{ value: 1, positive: true }} />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Tabs defaultValue="installed">
            <TabsList>
              <TabsTrigger value="installed" className="gap-1.5">
                <Package className="h-4 w-4" /> Installed
              </TabsTrigger>
              <TabsTrigger value="available" className="gap-1.5">
                <Store className="h-4 w-4" /> Available
              </TabsTrigger>
              <TabsTrigger value="updates" className="gap-1.5">
                <RefreshCw className="h-4 w-4" /> Updates
                {stats.updates > 0 && (
                  <Badge variant="default" className="ml-1 h-5 px-1.5 text-[10px]">{stats.updates}</Badge>
                )}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="installed">
              <Card>
                <CardContent className="p-0">
                  <DataTable
                    columns={installedColumns}
                    data={extList}
                    emptyMessage="No extensions installed"
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="available">
              <Card>
                <CardContent>
                  <EmptyState
                    icon={Store}
                    title="Extension Marketplace"
                    description="Browse and install extensions from the marketplace to extend JARVIS capabilities"
                    action={<Button size="sm" className="gap-1.5"><Download className="h-4 w-4" /> Browse Marketplace</Button>}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="updates">
              <Card>
                <CardContent className="p-0">
                  {updatableList.length > 0 ? (
                    <DataTable
                      columns={updatesColumns}
                      data={updatableList}
                      emptyMessage="All extensions are up to date"
                    />
                  ) : (
                    <EmptyState
                      icon={CheckCircle}
                      title="All Up to Date"
                      description="All your extensions are running the latest versions"
                    />
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </motion.div>
    </div>
  );
}
