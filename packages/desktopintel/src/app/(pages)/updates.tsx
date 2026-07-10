"use client";

import { motion } from "framer-motion";
import { Download, RefreshCw, Package, Calendar, Radio, Hash } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { StatCard } from "@/components/shared/stat-card";
import { SectionHeader } from "@/components/shared/section-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { formatRelativeTime } from "@/lib/utils";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export function Updates() {
  const { state, checkUpdates, updateSettings } = useDesktopStore();
  const { updates } = state;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader
          title="Updates"
          description="Manage JARVIS version and release channels"
        />
      </motion.div>

      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium">Current Version</span>
          <Badge variant="default" className="text-sm px-3 py-1">
            v{updates.currentVersion}
          </Badge>
          {updates.updateAvailable && (
            <Badge variant="success">
              v{updates.availableVersion} available
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={updates.channel}
            onValueChange={(channel) => updateSettings({ general: { updateChannel: channel as "stable" | "beta" | "nightly" } } as any)}
          >
            <SelectTrigger className="w-[120px] h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="stable">Stable</SelectItem>
              <SelectItem value="beta">Beta</SelectItem>
              <SelectItem value="nightly">Nightly</SelectItem>
            </SelectContent>
          </Select>
          <Button size="sm" variant="outline" onClick={checkUpdates}>
            <RefreshCw className="h-3.5 w-3.5 mr-1" />
            Check
          </Button>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-4 gap-3">
        <StatCard title="Current Version" value={`v${updates.currentVersion}`} icon={Hash} />
        <StatCard title="Update Available" value={updates.updateAvailable ? "Yes" : "No"} icon={Download} />
        <StatCard title="Last Checked" value={updates.lastCheckedAt ? formatRelativeTime(updates.lastCheckedAt) : "Never"} icon={Calendar} />
        <StatCard title="Channel" value={updates.channel.charAt(0).toUpperCase() + updates.channel.slice(1)} icon={Radio} />
      </motion.div>

      {updates.updateAvailable && (
        <motion.div variants={itemVariants}>
          <Card className="border-status-success/30 bg-status-success/5">
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Package className="h-5 w-5 text-status-success" />
                <div>
                  <p className="text-sm font-medium">Update Available</p>
                  <p className="text-xs text-muted-foreground">
                    Version v{updates.availableVersion} is ready to install
                  </p>
                </div>
              </div>
              <Button size="sm">
                <Download className="h-3.5 w-3.5 mr-1" />
                Update Now
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Release Notes</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <Separator className="mb-3" />
            <div className="flex items-center justify-center py-8">
              <p className="text-xs text-muted-foreground">
                Release notes will be displayed here after checking for updates
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
