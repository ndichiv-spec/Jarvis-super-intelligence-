"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Shield, Key, Users, Link, CheckCircle, XCircle, RefreshCw, Trash2, ExternalLink } from "lucide-react";

interface SSOProvider {
  id: string;
  name: string;
  type: string;
  configured: boolean;
  enabled: boolean;
  clientId?: string;
  tenantId?: string;
  domain?: string;
}

const INITIAL_PROVIDERS: SSOProvider[] = [
  { id: "okta", name: "Okta", type: "OIDC", configured: false, enabled: false },
  { id: "azure", name: "Azure AD", type: "OIDC", configured: false, enabled: false },
  { id: "google", name: "Google", type: "OAuth2", configured: false, enabled: false },
  { id: "saml", name: "SAML 2.0", type: "SAML", configured: false, enabled: false },
];

export default function EnterpriseSSOPage() {
  const [providers, setProviders] = useState<SSOProvider[]>(INITIAL_PROVIDERS);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [configuring, setConfiguring] = useState(false);
  const [config, setConfig] = useState({
    clientId: "",
    clientSecret: "",
    tenantId: "",
    domain: "",
    redirectUri: "http://localhost:3000/api/v1/auth/callback",
  });

  const updateProvider = (id: string, updates: Partial<SSOProvider>) => {
    setProviders(prev => prev.map(p => p.id === id ? { ...p, ...updates } : p));
  };

  const saveProviderConfig = async () => {
    if (!selectedProvider) return;

    setConfiguring(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      updateProvider(selectedProvider, {
        configured: true,
        clientId: config.clientId,
        tenantId: config.tenantId,
        domain: config.domain,
      });

      toast.success(`${selectedProvider.toUpperCase()} SSO configured`);
    } catch (error) {
      toast.error("Failed to save configuration");
    } finally {
      setConfiguring(false);
    }
  };

  const toggleProvider = (id: string) => {
    const provider = providers.find(p => p.id === id);
    if (provider && provider.configured) {
      updateProvider(id, { enabled: !provider.enabled });
      toast.success(`SSO ${provider.enabled ? "disabled" : "enabled"}`);
    } else {
      setSelectedProvider(id);
    }
  };

  const testConnection = async (id: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/enterprise/sso/test`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider: id }),
        }
      );

      const data = await response.json();
      if (data.success) {
        toast.success("Connection successful");
      } else {
        toast.error("Connection failed");
      }
    } catch (error) {
      toast.error("Connection test failed");
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500">
          <Shield className="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">Enterprise SSO</h1>
          <p className="text-muted-foreground">Configure single sign-on authentication</p>
        </div>
      </div>

      <Tabs defaultValue="providers" className="space-y-4">
        <TabsList>
          <TabsTrigger value="providers">Providers</TabsTrigger>
          <TabsTrigger value="settings">Global Settings</TabsTrigger>
          <TabsTrigger value="sessions">Active Sessions</TabsTrigger>
        </TabsList>

        <TabsContent value="providers">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providers.map((provider) => (
              <Card key={provider.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <CardTitle>{provider.name}</CardTitle>
                      <Badge variant="outline">{provider.type}</Badge>
                    </div>
                    {provider.configured ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>
                  <CardDescription>
                    {provider.configured ? "Configured and ready" : "Not configured"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={provider.enabled}
                        onCheckedChange={() => toggleProvider(provider.id)}
                        disabled={!provider.configured}
                      />
                      <Label>Enable</Label>
                    </div>
                    <div className="flex gap-2">
                      {provider.configured && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => testConnection(provider.id)}
                        >
                          <RefreshCw className="w-4 h-4 mr-1" />
                          Test
                        </Button>
                      )}
                      <Button
                        variant={provider.configured ? "outline" : "default"}
                        size="sm"
                        onClick={() => setSelectedProvider(provider.id)}
                      >
                        {provider.configured ? (
                          <Key className="w-4 h-4 mr-1" />
                        ) : (
                          <Link className="w-4 h-4 mr-1" />
                        )}
                        {provider.configured ? "Configure" : "Setup"}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {selectedProvider && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Configure {selectedProvider.toUpperCase()}</CardTitle>
                <CardDescription>Enter your SSO credentials</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Client ID</Label>
                    <Input
                      placeholder="Enter client ID"
                      value={config.clientId}
                      onChange={(e) => setConfig({ ...config, clientId: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Client Secret</Label>
                    <Input
                      type="password"
                      placeholder="Enter client secret"
                      value={config.clientSecret}
                      onChange={(e) => setConfig({ ...config, clientSecret: e.target.value })}
                    />
                  </div>
                  {(selectedProvider === "okta" || selectedProvider === "azure") && (
                    <div className="space-y-2">
                      <Label>Tenant ID / Domain</Label>
                      <Input
                        placeholder={selectedProvider === "okta" ? "your-domain.okta.com" : "tenant-id"}
                        value={config.tenantId || config.domain}
                        onChange={(e) => setConfig({
                          ...config,
                          [selectedProvider === "okta" ? "domain" : "tenantId"]: e.target.value
                        })}
                      />
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label>Redirect URI</Label>
                    <Input value={config.redirectUri} disabled />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={saveProviderConfig} disabled={configuring}>
                    {configuring ? "Saving..." : "Save Configuration"}
                  </Button>
                  <Button variant="outline" onClick={() => setSelectedProvider(null)}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Global SSO Settings</CardTitle>
              <CardDescription>Configure global authentication settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Enable SSO by default</Label>
                  <p className="text-sm text-muted-foreground">Require SSO for all users</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-provision users</Label>
                  <p className="text-sm text-muted-foreground">Create accounts for new SSO users</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Sync group memberships</Label>
                  <p className="text-sm text-muted-foreground">Sync groups from identity provider</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Session lifetime</Label>
                  <p className="text-sm text-muted-foreground">Hours before re-authentication</p>
                </div>
                <Input type="number" defaultValue="8" className="w-24" />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Allow password fallback</Label>
                  <p className="text-sm text-muted-foreground">Allow local password login</p>
                </div>
                <Switch />
              </div>

              <Button>Save Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sessions">
          <Card>
            <CardHeader>
              <CardTitle>Active SSO Sessions</CardTitle>
              <CardDescription>Users currently logged in via SSO</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No active sessions</p>
                <p className="text-sm">Sessions will appear here when users log in via SSO</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}