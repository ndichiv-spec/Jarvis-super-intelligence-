"use client";

import { motion } from "framer-motion";
import { FileText, CheckCircle2, Clock, Ban, FolderOpen } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { StatCard } from "@/components/shared/stat-card";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime, formatBytes } from "@/lib/utils";
import type { FileOperation } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function FileInteraction() {
  const { fileOperations } = useDesktopStore();

  const totalOps = fileOperations.length;
  const completedOps = fileOperations.filter((o) => o.status === "completed").length;
  const pendingOps = fileOperations.filter((o) => o.status === "pending" || o.status === "approved").length;
  const deniedOps = fileOperations.filter((o) => o.status === "denied").length;
  const successRate = totalOps > 0 ? Math.round((completedOps / totalOps) * 100) : 0;

  const statusBadge = (status: FileOperation["status"]) => {
    const map: Record<string, "success" | "warning" | "secondary" | "destructive" | "default"> = {
      completed: "success",
      approved: "info",
      pending: "warning",
      denied: "destructive",
      error: "destructive",
    };
    return <Badge variant={map[status] || "secondary"}>{status}</Badge>;
  };

  const columns: Column<FileOperation>[] = [
    {
      key: "type", header: "Type", sortable: true, render: (op) => (
        <Badge variant="outline" className="uppercase text-[10px]">{op.type}</Badge>
      ),
    },
    { key: "path", header: "Path", render: (op) => <span className="font-mono text-[11px]">{op.path}</span> },
    { key: "status", header: "Status", sortable: true, render: (op) => statusBadge(op.status) },
    { key: "size", header: "Size", sortable: true, render: (op) => <span className="text-muted-foreground">{formatBytes(op.size)}</span> },
    { key: "mimeType", header: "MIME Type", render: (op) => <span className="text-muted-foreground text-[11px]">{op.mimeType}</span> },
    { key: "timestamp", header: "Timestamp", sortable: true, render: (op) => <span className="text-muted-foreground">{formatRelativeTime(op.timestamp)}</span> },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="File Operations"
          description="Monitor file access and operations"
        />
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-3">
        <StatCard title="Total Operations" value={totalOps} icon={FileText} />
        <StatCard title="Success Rate" value={`${successRate}%`} icon={CheckCircle2} trend={successRate >= 80 ? { value: "Good", positive: true } : { value: "Low", positive: false }} />
        <StatCard title="Pending" value={pendingOps} icon={Clock} />
        <StatCard title="Denied" value={deniedOps} icon={Ban} />
      </motion.div>

      <motion.div variants={itemVariants}>
        {fileOperations.length === 0 ? (
          <EmptyState
            icon={FolderOpen}
            title="No file operations"
            description="File operations will appear here as JARVIS interacts with your files"
          />
        ) : (
          <DataTable columns={columns} data={fileOperations} keyField="id" />
        )}
      </motion.div>
    </motion.div>
  );
}
