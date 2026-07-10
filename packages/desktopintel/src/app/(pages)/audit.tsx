"use client";

import { motion } from "framer-motion";
import { ClipboardList, Download, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { DataTable, type Column } from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/utils";
import type { AuditEvent } from "@/types";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function AuditLog() {
  const { auditEvents } = useDesktopStore();

  const resultIcon = (result: AuditEvent["result"]) => {
    if (result === "allowed") return <CheckCircle className="h-3.5 w-3.5 text-status-success" />;
    if (result === "denied") return <XCircle className="h-3.5 w-3.5 text-status-error" />;
    return <AlertTriangle className="h-3.5 w-3.5 text-status-warning" />;
  };

  const columns: Column<AuditEvent>[] = [
    { key: "action", header: "Action", sortable: true, render: (e) => <span className="font-medium">{e.action}</span> },
    { key: "module", header: "Module", render: (e) => <Badge variant="secondary">{e.module}</Badge> },
    { key: "permission", header: "Permission", render: (e) => <span className="text-muted-foreground">{e.permission}</span> },
    { key: "resource", header: "Resource", render: (e) => <span className="text-muted-foreground text-[11px] font-mono">{e.resource}</span> },
    {
      key: "result", header: "Result", sortable: true, render: (e) => (
        <div className="flex items-center gap-1.5">
          {resultIcon(e.result)}
          <Badge
            variant={e.result === "allowed" ? "success" : e.result === "denied" ? "destructive" : "warning"}
            className="capitalize"
          >
            {e.result}
          </Badge>
        </div>
      ),
    },
    { key: "timestamp", header: "Timestamp", sortable: true, render: (e) => <span className="text-muted-foreground">{formatRelativeTime(e.timestamp)}</span> },
    { key: "details", header: "Details", render: (e) => <span className="text-muted-foreground text-[11px]">{e.details}</span> },
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
          title="Audit Log"
          description="Track all security and permission events across JARVIS"
          action={
            auditEvents.length > 0 && (
              <Button size="sm" variant="outline">
                <Download className="h-3.5 w-3.5 mr-1" />
                Export
              </Button>
            )
          }
        />
      </motion.div>

      <motion.div variants={itemVariants}>
        {auditEvents.length === 0 ? (
          <EmptyState
            icon={ClipboardList}
            title="No audit events"
            description="Audit events will be recorded here as JARVIS performs actions"
          />
        ) : (
          <DataTable columns={columns} data={auditEvents} keyField="id" />
        )}
      </motion.div>
    </motion.div>
  );
}
