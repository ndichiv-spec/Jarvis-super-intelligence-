"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Monitor, Globe, Play, Pause, RefreshCw, Square,
  Code, Eye, EyeOff, Settings, Maximize2, Minimize2,
  Plus, X, Navigation, Download, Upload, Terminal,
  Zap, Brain, Cpu, Wifi, WifiOff, AlertCircle,
  CheckCircle, Clock, FileText, Link, ExternalLink
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

interface BrowserWindow {
  id: string;
  title: string;
  visible: boolean;
  url: string;
  created_at: string;
}

interface BrowserStatus {
  initialized: boolean;
  running: boolean;
  windows: number;
  window_list: BrowserWindow[];
  message: string;
}

interface BrowserSettings {
  javascript_enabled: boolean;
  cookies_enabled: boolean;
  plugins_enabled: boolean;
  images_enabled: boolean;
  popups_blocked: boolean;
  user_agent: string;
  home_page: string;
  private_browsing: boolean;
}

export default function EmbeddedBrowser() {
  const [activeTab, setActiveTab] = useState("control");
  const [browserStatus, setBrowserStatus] = useState<BrowserStatus | null>(null);
  const [windows, setWindows] = useState<BrowserWindow[]>([]);
  const [selectedWindow, setSelectedWindow] = useState<string>("main");
  const [url, setUrl] = useState("http://localhost:3000");
  const [htmlContent, setHtmlContent] = useState("");
  const [scriptContent, setScriptContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState<BrowserSettings>({
    javascript_enabled: true,
    cookies_enabled: true,
    plugins_enabled: true,
    images_enabled: true,
    popups_blocked: true,
    user_agent: "JARVIS-Browser/1.0 (Self-Contained)",
    home_page: "http://localhost:3000",
    private_browsing: false
  });

  // API calls
  const initializeBrowser = useCallback(async () => {
    try {
      const response = await fetch("/api/browser/system/initialize", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        await fetchBrowserStatus();
      } else {
        // Don't throw error, just log it
        console.warn("Browser initialization returned non-OK status");
        await fetchBrowserStatus();
      }
    } catch (error) {
      // Don't block dashboard loading, just log error
      console.warn("Browser initialization skipped:", error);
      toast.info("Browser system unavailable - dashboard still functional");
    }
  }, []);

  const fetchBrowserStatus = useCallback(async () => {
    try {
      const response = await fetch("/api/browser/system/status");
      if (response.ok) {
        const status = await response.json();
        setBrowserStatus(status);
        setWindows(status.window_list || []);
      }
    } catch (error) {
      console.error("Failed to fetch browser status:", error);
    }
  }, []);

  const createWindow = useCallback(async (windowId: string) => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/browser/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ window_id: windowId })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        await fetchBrowserStatus();
      } else {
        // Don't throw error, just log it
        console.warn("Window creation returned non-OK status");
      }
    } catch (error) {
      // Don't block dashboard loading, just log error
      console.warn("Window creation skipped:", error);
      toast.info("Browser window creation unavailable - dashboard still functional");
    } finally {
      setIsLoading(false);
    }
  }, [fetchBrowserStatus]);

  const navigateToUrl = useCallback(async (windowId: string, targetUrl: string) => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/browser/navigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ window_id: windowId, url: targetUrl })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
      } else {
        throw new Error("Failed to navigate");
      }
    } catch (error) {
      toast.error("Failed to navigate to URL");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadHtmlContent = useCallback(async (windowId: string, html: string) => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/browser/load-content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ window_id: windowId, html, base_url: "" })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
      } else {
        throw new Error("Failed to load content");
      }
    } catch (error) {
      toast.error("Failed to load HTML content");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const executeScript = useCallback(async (windowId: string, script: string) => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/browser/execute-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ window_id: windowId, script })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
      } else {
        throw new Error("Failed to execute script");
      }
    } catch (error) {
      toast.error("Failed to execute JavaScript");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const showWindow = useCallback(async (windowId: string) => {
    try {
      const response = await fetch(`/api/browser/${windowId}/show`, {
        method: "POST"
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        await fetchBrowserStatus();
      }
    } catch (error) {
      toast.error("Failed to show window");
      console.error(error);
    }
  }, [fetchBrowserStatus]);

  const hideWindow = useCallback(async (windowId: string) => {
    try {
      const response = await fetch(`/api/browser/${windowId}/hide`, {
        method: "POST"
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        await fetchBrowserStatus();
      }
    } catch (error) {
      toast.error("Failed to hide window");
      console.error(error);
    }
  }, [fetchBrowserStatus]);

  const closeWindow = useCallback(async (windowId: string) => {
    try {
      const response = await fetch(`/api/browser/${windowId}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        await fetchBrowserStatus();
      }
    } catch (error) {
      toast.error("Failed to close window");
      console.error(error);
    }
  }, [fetchBrowserStatus]);

  // Initialize on mount
  useEffect(() => {
    fetchBrowserStatus();
    const interval = setInterval(fetchBrowserStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, [fetchBrowserStatus]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500 rounded-lg">
                <Monitor className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">JARVIS Embedded Browser</h1>
                <p className="text-gray-300">Self-contained browser system - no external dependencies</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant={browserStatus?.running ? "default" : "secondary"}>
                {browserStatus?.running ? (
                  <>
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Active
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Inactive
                  </>
                )}
              </Badge>
              
              <Button onClick={initializeBrowser} disabled={isLoading}>
                <Cpu className="w-4 h-4 mr-2" />
                Initialize
              </Button>
            </div>
          </div>

          {/* Status Card */}
          <Card className="mb-6 bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Browser System Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{browserStatus?.windows || 0}</div>
                  <div className="text-sm text-gray-400">Active Windows</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {browserStatus?.running ? "Online" : "Offline"}
                  </div>
                  <div className="text-sm text-gray-400">System Status</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400">Qt5/6</div>
                  <div className="text-sm text-gray-400">Engine</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-400">Self-Contained</div>
                  <div className="text-sm text-gray-400">Type</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Main Controls */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 bg-slate-800">
              <TabsTrigger value="control" className="data-[state=active]:bg-slate-700">
                <Settings className="w-4 h-4 mr-2" />
                Control
              </TabsTrigger>
              <TabsTrigger value="windows" className="data-[state=active]:bg-slate-700">
                <Monitor className="w-4 h-4 mr-2" />
                Windows
              </TabsTrigger>
              <TabsTrigger value="content" className="data-[state=active]:bg-slate-700">
                <Code className="w-4 h-4 mr-2" />
                Content
              </TabsTrigger>
              <TabsTrigger value="advanced" className="data-[state=active]:bg-slate-700">
                <Terminal className="w-4 h-4 mr-2" />
                Advanced
              </TabsTrigger>
            </TabsList>

            {/* Control Tab */}
            <TabsContent value="control">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Browser Control</CardTitle>
                  <CardDescription>Manage browser windows and navigation</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Quick Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Button 
                      onClick={() => createWindow(`window-${Date.now()}`)}
                      disabled={isLoading}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create Window
                    </Button>
                    
                    <Button 
                      onClick={() => navigateToUrl(selectedWindow, url)}
                      disabled={isLoading || !browserStatus?.running}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Navigation className="w-4 h-4 mr-2" />
                      Navigate
                    </Button>
                    
                    <Button 
                      onClick={() => showWindow(selectedWindow)}
                      disabled={isLoading || !browserStatus?.running}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Show Window
                    </Button>
                  </div>

                  {/* URL Input */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Target URL</label>
                    <div className="flex space-x-2">
                      <Input
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Enter URL to navigate to..."
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                      <Button
                        onClick={() => navigateToUrl(selectedWindow, url)}
                        disabled={isLoading || !browserStatus?.running}
                      >
                        <Globe className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Window Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">Target Window</label>
                    <select
                      value={selectedWindow}
                      onChange={(e) => setSelectedWindow(e.target.value)}
                      className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-white"
                    >
                      {windows.map((window) => (
                        <option key={window.id} value={window.id}>
                          {window.id} - {window.title}
                        </option>
                      ))}
                    </select>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Windows Tab */}
            <TabsContent value="windows">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Browser Windows</CardTitle>
                  <CardDescription>Manage individual browser windows</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {windows.length === 0 ? (
                      <div className="text-center py-8 text-gray-400">
                        <Monitor className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No browser windows created</p>
                        <Button onClick={() => createWindow("main")} className="mt-4">
                          Create First Window
                        </Button>
                      </div>
                    ) : (
                      windows.map((window) => (
                        <div key={window.id} className="flex items-center justify-between p-4 bg-slate-700 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Monitor className="w-5 h-5 text-blue-400" />
                            <div>
                              <div className="text-white font-medium">{window.id}</div>
                              <div className="text-sm text-gray-400">{window.title}</div>
                              <div className="text-xs text-gray-500">{window.url}</div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Badge variant={window.visible ? "default" : "secondary"}>
                              {window.visible ? "Visible" : "Hidden"}
                            </Badge>
                            
                            <Button
                              size="sm"
                              onClick={() => showWindow(window.id)}
                              disabled={isLoading}
                            >
                              <Eye className="w-3 h-3" />
                            </Button>
                            
                            <Button
                              size="sm"
                              onClick={() => hideWindow(window.id)}
                              disabled={isLoading}
                            >
                              <EyeOff className="w-3 h-3" />
                            </Button>
                            
                            <Button
                              size="sm"
                              onClick={() => closeWindow(window.id)}
                              disabled={isLoading}
                              variant="destructive"
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Content Tab */}
            <TabsContent value="content">
              <div className="space-y-6">
                {/* HTML Content */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Load HTML Content</CardTitle>
                    <CardDescription>Load custom HTML content into browser</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      value={htmlContent}
                      onChange={(e) => setHtmlContent(e.target.value)}
                      placeholder="Enter HTML content to load..."
                      className="min-h-[200px] bg-slate-700 border-slate-600 text-white"
                    />
                    <Button
                      onClick={() => loadHtmlContent(selectedWindow, htmlContent)}
                      disabled={isLoading || !browserStatus?.running}
                      className="w-full"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Load HTML
                    </Button>
                  </CardContent>
                </Card>

                {/* JavaScript Execution */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Execute JavaScript</CardTitle>
                    <CardDescription>Run JavaScript code in browser context</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Textarea
                      value={scriptContent}
                      onChange={(e) => setScriptContent(e.target.value)}
                      placeholder="Enter JavaScript code to execute..."
                      className="min-h-[150px] bg-slate-700 border-slate-600 text-white"
                    />
                    <Button
                      onClick={() => executeScript(selectedWindow, scriptContent)}
                      disabled={isLoading || !browserStatus?.running}
                      className="w-full"
                    >
                      <Code className="w-4 h-4 mr-2" />
                      Execute Script
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Advanced Tab */}
            <TabsContent value="advanced">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Advanced Settings</CardTitle>
                  <CardDescription>Configure browser engine and system settings</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Browser Settings */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-white font-medium">Engine Settings</h3>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">JavaScript</label>
                        <input
                          type="checkbox"
                          checked={settings.javascript_enabled}
                          onChange={(e) => setSettings({...settings, javascript_enabled: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">Cookies</label>
                        <input
                          type="checkbox"
                          checked={settings.cookies_enabled}
                          onChange={(e) => setSettings({...settings, cookies_enabled: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">Plugins</label>
                        <input
                          type="checkbox"
                          checked={settings.plugins_enabled}
                          onChange={(e) => setSettings({...settings, plugins_enabled: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-white font-medium">Security Settings</h3>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">Block Popups</label>
                        <input
                          type="checkbox"
                          checked={settings.popups_blocked}
                          onChange={(e) => setSettings({...settings, popups_blocked: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">Private Browsing</label>
                        <input
                          type="checkbox"
                          checked={settings.private_browsing}
                          onChange={(e) => setSettings({...settings, private_browsing: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <label className="text-sm text-gray-300">Images</label>
                        <input
                          type="checkbox"
                          checked={settings.images_enabled}
                          onChange={(e) => setSettings({...settings, images_enabled: e.target.checked})}
                          className="rounded"
                        />
                      </div>
                    </div>
                  </div>

                  {/* System Information */}
                  <div className="mt-6 p-4 bg-slate-700 rounded-lg">
                    <h3 className="text-white font-medium mb-3">System Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Engine:</span>
                        <span className="text-white ml-2">QtWebEngine (Chromium)</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Version:</span>
                        <span className="text-white ml-2">JARVIS Browser 1.0</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Status:</span>
                        <span className="text-white ml-2">{browserStatus?.message || "Unknown"}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Windows:</span>
                        <span className="text-white ml-2">{browserStatus?.windows || 0}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}
