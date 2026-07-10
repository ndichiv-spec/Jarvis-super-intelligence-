"use client";

import { motion } from "framer-motion";
import { Palette, Bell, Wrench, WifiOff, Globe, Moon, Sun, Monitor, Type, Move, Sparkles } from "lucide-react";
import { useDesktopStore } from "@/stores/desktop-store";
import { SectionHeader } from "@/components/shared/section-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

function SettingRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-2">
      <div>
        <p className="text-sm">{label}</p>
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

export function SettingsPage() {
  const { settings, updateSettings } = useDesktopStore();

  if (!settings) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-xs text-muted-foreground">Loading settings...</p>
      </div>
    );
  }

  const { appearance, notifications, workspace, offline, general } = settings;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4 max-w-2xl"
    >
      <motion.div variants={itemVariants}>
        <SectionHeader title="Settings" description="Configure JARVIS to your preferences" />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-1">
            <SettingRow label="Theme" description="Choose your preferred appearance">
              <Select
                value={appearance.theme}
                onValueChange={(theme) => updateSettings({ appearance: { ...appearance, theme: theme as "light" | "dark" | "system" } })}
              >
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">
                    <div className="flex items-center gap-2"><Sun className="h-3.5 w-3.5" /> Light</div>
                  </SelectItem>
                  <SelectItem value="dark">
                    <div className="flex items-center gap-2"><Moon className="h-3.5 w-3.5" /> Dark</div>
                  </SelectItem>
                  <SelectItem value="system">
                    <div className="flex items-center gap-2"><Monitor className="h-3.5 w-3.5" /> System</div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            <Separator />
            <SettingRow label="Font Size" description="Adjust text size across the interface">
              <Select
                value={appearance.fontSize}
                onValueChange={(fontSize) => updateSettings({ appearance: { ...appearance, fontSize: fontSize as "small" | "medium" | "large" } })}
              >
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="small">Small</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="large">Large</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            <Separator />
            <SettingRow label="Reduced Motion" description="Minimize animations and transitions">
              <Switch
                checked={appearance.reducedMotion}
                onCheckedChange={(checked) => updateSettings({ appearance: { ...appearance, reducedMotion: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Compact Mode" description="Display more content with reduced spacing">
              <Switch
                checked={appearance.compactMode}
                onCheckedChange={(checked) => updateSettings({ appearance: { ...appearance, compactMode: checked } })}
              />
            </SettingRow>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-1">
            <SettingRow label="Enable Notifications" description="Master toggle for all notifications">
              <Switch
                checked={notifications.enabled}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, enabled: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Workflow Complete" description="Notify when workflows finish">
              <Switch
                checked={notifications.workflowComplete}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, workflowComplete: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Agent Requests" description="Notify when agents request input">
              <Switch
                checked={notifications.agentRequests}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, agentRequests: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Security Alerts" description="Notify on security events">
              <Switch
                checked={notifications.securityAlerts}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, securityAlerts: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Automation Updates" description="Notify on automation changes">
              <Switch
                checked={notifications.automationUpdates}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, automationUpdates: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="System Messages" description="Notify on system events">
              <Switch
                checked={notifications.systemMessages}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, systemMessages: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Sound" description="Play sound for notifications">
              <Switch
                checked={notifications.soundEnabled}
                onCheckedChange={(checked) => updateSettings({ notifications: { ...notifications, soundEnabled: checked } })}
              />
            </SettingRow>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Workspace
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-1">
            <SettingRow label="Default Workspace" description="Workspace to load on startup">
              <Input
                className="w-[200px] h-8 text-xs"
                value={workspace.defaultWorkspace}
                onChange={(e) => updateSettings({ workspace: { ...workspace, defaultWorkspace: e.target.value } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Auto Sync" description="Automatically sync changes">
              <Switch
                checked={workspace.autoSync}
                onCheckedChange={(checked) => updateSettings({ workspace: { ...workspace, autoSync: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Sync Interval" description="Seconds between automatic syncs">
              <Input
                type="number"
                className="w-[100px] h-8 text-xs"
                value={workspace.syncInterval}
                onChange={(e) => updateSettings({ workspace: { ...workspace, syncInterval: parseInt(e.target.value) || 30 } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Confirm Before Action" description="Ask for confirmation before executing actions">
              <Switch
                checked={workspace.confirmBeforeAction}
                onCheckedChange={(checked) => updateSettings({ workspace: { ...workspace, confirmBeforeAction: checked } })}
              />
            </SettingRow>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <WifiOff className="h-4 w-4" />
              Offline
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-1">
            <SettingRow label="Enable Offline Mode" description="Allow operation without network">
              <Switch
                checked={offline.enableOfflineMode}
                onCheckedChange={(checked) => updateSettings({ offline: { ...offline, enableOfflineMode: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Cache Conversations" description="Store conversations for offline access">
              <Switch
                checked={offline.cacheConversations}
                onCheckedChange={(checked) => updateSettings({ offline: { ...offline, cacheConversations: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Cache Knowledge" description="Store knowledge base for offline access">
              <Switch
                checked={offline.cacheKnowledge}
                onCheckedChange={(checked) => updateSettings({ offline: { ...offline, cacheKnowledge: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Cache Limit" description="Maximum cache size (MB)">
              <Input
                type="number"
                className="w-[100px] h-8 text-xs"
                value={Math.round(offline.cacheLimit / (1024 * 1024))}
                onChange={(e) => updateSettings({ offline: { ...offline, cacheLimit: (parseInt(e.target.value) || 100) * 1024 * 1024 } })}
              />
            </SettingRow>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              General
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-1">
            <SettingRow label="Language" description="Interface language">
              <Select
                value={general.language}
                onValueChange={(language) => updateSettings({ general: { ...general, language } })}
              >
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="zh-CN">简体中文</SelectItem>
                  <SelectItem value="ja">日本語</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            <Separator />
            <SettingRow label="Telemetry" description="Send anonymous usage data to improve JARVIS">
              <Switch
                checked={general.telemetryEnabled}
                onCheckedChange={(checked) => updateSettings({ general: { ...general, telemetryEnabled: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Auto Update" description="Automatically install updates">
              <Switch
                checked={general.autoUpdate}
                onCheckedChange={(checked) => updateSettings({ general: { ...general, autoUpdate: checked } })}
              />
            </SettingRow>
            <Separator />
            <SettingRow label="Update Channel" description="Release channel for updates">
              <Select
                value={general.updateChannel}
                onValueChange={(channel) => updateSettings({ general: { ...general, updateChannel: channel as "stable" | "beta" | "nightly" } })}
              >
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="stable">Stable</SelectItem>
                  <SelectItem value="beta">Beta</SelectItem>
                  <SelectItem value="nightly">Nightly</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
            <Separator />
            <SettingRow label="Log Level" description="Verbosity of logging output">
              <Select
                value={general.logLevel}
                onValueChange={(logLevel) => updateSettings({ general: { ...general, logLevel: logLevel as "debug" | "info" | "warn" | "error" } })}
              >
                <SelectTrigger className="w-[130px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="debug">Debug</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                  <SelectItem value="warn">Warning</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
