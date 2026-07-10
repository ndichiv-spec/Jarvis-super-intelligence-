"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sliders,
  Bot,
  Brain,
  Shield,
  Bell,
  Monitor,
  Beaker,
  Save,
  RotateCcw,
} from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    fontSize: "medium",
    reducedMotion: false,
    autoSave: true,
    showTimestamps: true,
    model: "gpt-4",
    temperature: 0.7,
    maxTokens: 4096,
    autoArchive: true,
    confidenceThreshold: 0.3,
    twoFactor: false,
    sessionTimeout: 30,
    emailNotifications: true,
    desktopNotifications: true,
    workflowNotifications: true,
    agentUpdates: true,
    securityAlerts: true,
    experimental: false,
  });

  const toggle = (key: keyof typeof settings) => {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="pb-8">
      <PageHeader title="Settings" description="Configure your JARVIS platform preferences" />

      <div className="px-6">
        <Tabs defaultValue="platform" className="space-y-4">
          <TabsList className="w-full justify-start overflow-x-auto">
            <TabsTrigger value="platform"><Sliders className="mr-2 h-4 w-4" /> Platform</TabsTrigger>
            <TabsTrigger value="ai"><Bot className="mr-2 h-4 w-4" /> AI Runtime</TabsTrigger>
            <TabsTrigger value="memory"><Brain className="mr-2 h-4 w-4" /> Memory</TabsTrigger>
            <TabsTrigger value="security"><Shield className="mr-2 h-4 w-4" /> Security</TabsTrigger>
            <TabsTrigger value="notifications"><Bell className="mr-2 h-4 w-4" /> Notifications</TabsTrigger>
            <TabsTrigger value="accessibility"><Monitor className="mr-2 h-4 w-4" /> Accessibility</TabsTrigger>
            <TabsTrigger value="experimental"><Beaker className="mr-2 h-4 w-4" /> Experimental</TabsTrigger>
          </TabsList>

          <TabsContent value="platform" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Platform Preferences</CardTitle>
                <CardDescription>General platform behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Font Size</p><p className="text-xs text-muted-foreground">Interface text size</p></div>
                  <Select value={settings.fontSize} onValueChange={(v) => setSettings((s) => ({ ...s, fontSize: v }))}>
                    <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="small">Small</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="large">Large</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Auto-Save</p><p className="text-xs text-muted-foreground">Automatically save workspace state</p></div>
                  <Switch checked={settings.autoSave} onCheckedChange={() => toggle("autoSave")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Show Timestamps</p><p className="text-xs text-muted-foreground">Display timestamps in conversations</p></div>
                  <Switch checked={settings.showTimestamps} onCheckedChange={() => toggle("showTimestamps")} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">AI Runtime Configuration</CardTitle>
                <CardDescription>Model selection and generation parameters</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Default Model</p><p className="text-xs text-muted-foreground">Primary AI model for conversations</p></div>
                  <Select value={settings.model} onValueChange={(v) => setSettings((s) => ({ ...s, model: v }))}>
                    <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4">GPT-4</SelectItem>
                      <SelectItem value="gpt-3.5">GPT-3.5</SelectItem>
                      <SelectItem value="claude-3">Claude 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Temperature</p><p className="text-xs text-muted-foreground">Controls randomness (0 = deterministic, 1 = creative)</p></div>
                  <Select value={settings.temperature.toString()} onValueChange={(v) => setSettings((s) => ({ ...s, temperature: parseFloat(v) }))}>
                    <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0.0">0.0 (Precise)</SelectItem>
                      <SelectItem value="0.3">0.3 (Focused)</SelectItem>
                      <SelectItem value="0.7">0.7 (Balanced)</SelectItem>
                      <SelectItem value="1.0">1.0 (Creative)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Max Tokens</p><p className="text-xs text-muted-foreground">Maximum response length</p></div>
                  <Select value={settings.maxTokens.toString()} onValueChange={(v) => setSettings((s) => ({ ...s, maxTokens: parseInt(v) }))}>
                    <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1024">1,024</SelectItem>
                      <SelectItem value="2048">2,048</SelectItem>
                      <SelectItem value="4096">4,096</SelectItem>
                      <SelectItem value="8192">8,192</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="memory" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Memory Preferences</CardTitle>
                <CardDescription>Control how JARVIS remembers information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Auto-Archive Low Confidence</p><p className="text-xs text-muted-foreground">Automatically archive memories below confidence threshold</p></div>
                  <Switch checked={settings.autoArchive} onCheckedChange={() => toggle("autoArchive")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Confidence Threshold</p><p className="text-xs text-muted-foreground">Minimum confidence score for active memories</p></div>
                  <Select value={settings.confidenceThreshold.toString()} onValueChange={(v) => setSettings((s) => ({ ...s, confidenceThreshold: parseFloat(v) }))}>
                    <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0.1">0.1 (Lenient)</SelectItem>
                      <SelectItem value="0.3">0.3 (Moderate)</SelectItem>
                      <SelectItem value="0.5">0.5 (Balanced)</SelectItem>
                      <SelectItem value="0.7">0.7 (Strict)</SelectItem>
                      <SelectItem value="0.9">0.9 (Very Strict)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Security Preferences</CardTitle>
                <CardDescription>Manage your account security</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Two-Factor Authentication</p><p className="text-xs text-muted-foreground">Add an extra layer of security</p></div>
                  <Switch checked={settings.twoFactor} onCheckedChange={() => toggle("twoFactor")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Session Timeout</p><p className="text-xs text-muted-foreground">Automatically log out after inactivity</p></div>
                  <Select value={settings.sessionTimeout.toString()} onValueChange={(v) => setSettings((s) => ({ ...s, sessionTimeout: parseInt(v) }))}>
                    <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                      <SelectItem value="480">8 hours</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Notification Preferences</CardTitle>
                <CardDescription>Control what notifications you receive</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Email Notifications</p><p className="text-xs text-muted-foreground">Receive notifications via email</p></div>
                  <Switch checked={settings.emailNotifications} onCheckedChange={() => toggle("emailNotifications")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Desktop Notifications</p><p className="text-xs text-muted-foreground">Show notifications on desktop</p></div>
                  <Switch checked={settings.desktopNotifications} onCheckedChange={() => toggle("desktopNotifications")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Workflow Completion</p><p className="text-xs text-muted-foreground">Notify when workflows complete</p></div>
                  <Switch checked={settings.workflowNotifications} onCheckedChange={() => toggle("workflowNotifications")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Agent Updates</p><p className="text-xs text-muted-foreground">Notify about agent status changes</p></div>
                  <Switch checked={settings.agentUpdates} onCheckedChange={() => toggle("agentUpdates")} />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Security Alerts</p><p className="text-xs text-muted-foreground">Critical security notifications</p></div>
                  <Switch checked={settings.securityAlerts} onCheckedChange={() => toggle("securityAlerts")} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="accessibility" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Accessibility</CardTitle>
                <CardDescription>Accessibility and display preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Reduced Motion</p><p className="text-xs text-muted-foreground">Minimize animations and transitions</p></div>
                  <Switch checked={settings.reducedMotion} onCheckedChange={() => toggle("reducedMotion")} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="experimental" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Experimental Features</CardTitle>
                <CardDescription>Try out upcoming features (may be unstable)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div><p className="text-sm font-medium">Enable Experimental</p><p className="text-xs text-muted-foreground">Access features in development</p></div>
                  <Switch checked={settings.experimental} onCheckedChange={() => toggle("experimental")} />
                </div>
                {settings.experimental && (
                  <div className="rounded-md border border-status-warning/50 bg-status-warning/5 p-3">
                    <p className="text-xs text-status-warning">Experimental features may be unstable and are subject to change. Use with caution.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="flex items-center gap-2 mt-6">
          <Button>
            <Save className="mr-2 h-4 w-4" />
            Save All Settings
          </Button>
          <Button variant="outline">
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset to Defaults
          </Button>
        </div>
      </div>
    </div>
  );
}
