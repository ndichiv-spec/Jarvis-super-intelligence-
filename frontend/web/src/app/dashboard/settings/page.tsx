'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  Sun,
  Moon,
  Shield,
  Database,
  Globe,
  Trash2,
  Save,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useTheme } from 'next-themes';
import { ThemeSelector } from '@/components/theme-selector';
import {
  jarvisAPI,
  type ProviderFeatureStatus,
  type ProviderSettings,
} from '@/lib/api';

const DEFAULT_PROVIDER_SETTINGS: ProviderSettings = {
  ollama_base_url: 'http://localhost:11434',
  ollama_model: 'llama3',
  openai_api_key: '',
  google_gemini_api_key: '',
  anthropic_api_key: '',
  huggingface_api_key: '',
  stability_api_key: '',
  replicate_api_key: '',
  aws_access_key_id: '',
  aws_secret_access_key: '',
  aws_region: 'us-east-1',
  tavily_api_key: '',
  serper_api_key: '',
  news_api_key: '',
  openweathermap_api_key: '',
};

type LocalSettings = {
  watchdogInterval: number;
  autoRecovery: boolean;
  optimizationStrategy: string;
  maxMemoryPercent: number;
  schedulerInterval: number;
  enableNotifications: boolean;
  enableSounds: boolean;
  streamingResponses: boolean;
  autoSaveChat: boolean;
  defaultModel: string;
};

const DEFAULT_LOCAL_SETTINGS: LocalSettings = {
  watchdogInterval: 60,
  autoRecovery: true,
  optimizationStrategy: 'adaptive',
  maxMemoryPercent: 80,
  schedulerInterval: 10,
  enableNotifications: true,
  enableSounds: false,
  streamingResponses: true,
  autoSaveChat: true,
  defaultModel: 'local',
};

const PROVIDER_GROUPS = [
  {
    title: 'Local & LLM Providers',
    description: 'Configure the engines used for chat, reasoning, and OMEGA routing.',
    providers: ['ollama', 'openai', 'gemini', 'anthropic', 'huggingface'],
  },
  {
    title: 'Image & Vision Providers',
    description: 'Enable image generation and vision analysis features.',
    providers: ['stability', 'replicate', 'aws'],
  },
  {
    title: 'Search & Intelligence Providers',
    description: 'Connect search, news, and weather providers used by global intelligence features.',
    providers: ['tavily', 'serper', 'newsapi', 'weather'],
  },
];

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingProviders, setIsLoadingProviders] = useState(true);
  const [providerSettings, setProviderSettings] = useState<ProviderSettings>(DEFAULT_PROVIDER_SETTINGS);
  const [providerStatus, setProviderStatus] = useState<Record<string, ProviderFeatureStatus>>({});
  const [envPath, setEnvPath] = useState('');
  const [watchdogInterval, setWatchdogInterval] = useState([DEFAULT_LOCAL_SETTINGS.watchdogInterval]);
  const [autoRecovery, setAutoRecovery] = useState(DEFAULT_LOCAL_SETTINGS.autoRecovery);
  const [optimizationStrategy, setOptimizationStrategy] = useState(DEFAULT_LOCAL_SETTINGS.optimizationStrategy);
  const [maxMemoryPercent, setMaxMemoryPercent] = useState([DEFAULT_LOCAL_SETTINGS.maxMemoryPercent]);
  const [schedulerInterval, setSchedulerInterval] = useState([DEFAULT_LOCAL_SETTINGS.schedulerInterval]);
  const [enableNotifications, setEnableNotifications] = useState(DEFAULT_LOCAL_SETTINGS.enableNotifications);
  const [enableSounds, setEnableSounds] = useState(DEFAULT_LOCAL_SETTINGS.enableSounds);
  const [streamingResponses, setStreamingResponses] = useState(DEFAULT_LOCAL_SETTINGS.streamingResponses);
  const [autoSaveChat, setAutoSaveChat] = useState(DEFAULT_LOCAL_SETTINGS.autoSaveChat);
  const [defaultModel, setDefaultModel] = useState(DEFAULT_LOCAL_SETTINGS.defaultModel);

  useEffect(() => {
    loadLocalSettings();
    void loadProviderSettings();
  }, []);

  const loadLocalSettings = () => {
    try {
      const saved = localStorage.getItem('jarvis-settings');
      if (!saved) {
        return;
      }

      const parsed = JSON.parse(saved) as Partial<LocalSettings>;
      setWatchdogInterval([parsed.watchdogInterval ?? DEFAULT_LOCAL_SETTINGS.watchdogInterval]);
      setAutoRecovery(parsed.autoRecovery ?? DEFAULT_LOCAL_SETTINGS.autoRecovery);
      setOptimizationStrategy(parsed.optimizationStrategy ?? DEFAULT_LOCAL_SETTINGS.optimizationStrategy);
      setMaxMemoryPercent([parsed.maxMemoryPercent ?? DEFAULT_LOCAL_SETTINGS.maxMemoryPercent]);
      setSchedulerInterval([parsed.schedulerInterval ?? DEFAULT_LOCAL_SETTINGS.schedulerInterval]);
      setEnableNotifications(parsed.enableNotifications ?? DEFAULT_LOCAL_SETTINGS.enableNotifications);
      setEnableSounds(parsed.enableSounds ?? DEFAULT_LOCAL_SETTINGS.enableSounds);
      setStreamingResponses(parsed.streamingResponses ?? DEFAULT_LOCAL_SETTINGS.streamingResponses);
      setAutoSaveChat(parsed.autoSaveChat ?? DEFAULT_LOCAL_SETTINGS.autoSaveChat);
      setDefaultModel(parsed.defaultModel ?? DEFAULT_LOCAL_SETTINGS.defaultModel);
    } catch (error) {
      console.error('Failed to load local settings', error);
    }
  };

  const loadProviderSettings = async () => {
    setIsLoadingProviders(true);
    try {
      const response = await jarvisAPI.getProviderSettings();
      setProviderSettings(response.settings);
      setProviderStatus(response.providers);
      setEnvPath(response.env_path);
    } catch (error: any) {
      toast.error(`Failed to load provider settings: ${error.message}`);
    } finally {
      setIsLoadingProviders(false);
    }
  };

  const updateProviderField = (field: keyof ProviderSettings, value: string) => {
    setProviderSettings((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const localSettings: LocalSettings = {
        watchdogInterval: watchdogInterval[0],
        autoRecovery,
        optimizationStrategy,
        maxMemoryPercent: maxMemoryPercent[0],
        schedulerInterval: schedulerInterval[0],
        enableNotifications,
        enableSounds,
        streamingResponses,
        autoSaveChat,
        defaultModel,
      };
      localStorage.setItem('jarvis-settings', JSON.stringify(localSettings));

      const response = await jarvisAPI.updateProviderSettings(providerSettings);
      setProviderSettings(response.settings);
      setProviderStatus(response.providers);
      setEnvPath(response.env_path);
      toast.success('Settings saved successfully');
    } catch (error: any) {
      toast.error(`Failed to save settings: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    localStorage.removeItem('jarvis-settings');
    setWatchdogInterval([DEFAULT_LOCAL_SETTINGS.watchdogInterval]);
    setAutoRecovery(DEFAULT_LOCAL_SETTINGS.autoRecovery);
    setOptimizationStrategy(DEFAULT_LOCAL_SETTINGS.optimizationStrategy);
    setMaxMemoryPercent([DEFAULT_LOCAL_SETTINGS.maxMemoryPercent]);
    setSchedulerInterval([DEFAULT_LOCAL_SETTINGS.schedulerInterval]);
    setEnableNotifications(DEFAULT_LOCAL_SETTINGS.enableNotifications);
    setEnableSounds(DEFAULT_LOCAL_SETTINGS.enableSounds);
    setStreamingResponses(DEFAULT_LOCAL_SETTINGS.streamingResponses);
    setAutoSaveChat(DEFAULT_LOCAL_SETTINGS.autoSaveChat);
    setDefaultModel(DEFAULT_LOCAL_SETTINGS.defaultModel);
    await loadProviderSettings();
    toast.info('Local preferences reset. Provider settings were reloaded from the backend.');
  };

  const configuredProviders = Object.values(providerStatus).filter((provider) => provider.configured).length;

  return (
    <div className="flex-1 space-y-6 p-6 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="h-8 w-8" />
            Settings
          </h1>
          <p className="text-muted-foreground">Configure JARVIS behavior, appearance, and provider integrations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            <Trash2 className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
            Save Settings
          </Button>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <ThemeSelector />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                Appearance
              </CardTitle>
              <CardDescription>Customize the look and feel</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Dark Mode</Label>
                  <p className="text-xs text-muted-foreground">Toggle dark/light theme</p>
                </div>
                <Switch
                  checked={theme === 'dark'}
                  onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')}
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label>Notifications</Label>
                  <p className="text-xs text-muted-foreground">Show desktop notifications</p>
                </div>
                <Switch checked={enableNotifications} onCheckedChange={setEnableNotifications} />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label>Sound Effects</Label>
                  <p className="text-xs text-muted-foreground">Play sounds for events</p>
                </div>
                <Switch checked={enableSounds} onCheckedChange={setEnableSounds} />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Chat & Responses
              </CardTitle>
              <CardDescription>Configure chat behavior and AI model preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Default Model</Label>
                <Select value={defaultModel} onValueChange={setDefaultModel}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="local">Local (Ollama)</SelectItem>
                    <SelectItem value="openai">OpenAI</SelectItem>
                    <SelectItem value="gemini">Google Gemini</SelectItem>
                    <SelectItem value="auto">Auto Select</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label>Streaming Responses</Label>
                  <p className="text-xs text-muted-foreground">Show responses as they generate</p>
                </div>
                <Switch checked={streamingResponses} onCheckedChange={setStreamingResponses} />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-Save Chat</Label>
                  <p className="text-xs text-muted-foreground">Automatically save chat history</p>
                </div>
                <Switch checked={autoSaveChat} onCheckedChange={setAutoSaveChat} />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Provider Overview
              </CardTitle>
              <CardDescription>Backend-backed provider settings stored in the local environment file</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Configured Providers</Label>
                  <p className="text-xs text-muted-foreground">Detected from the backend runtime configuration</p>
                </div>
                <Badge variant={configuredProviders > 0 ? 'default' : 'secondary'}>
                  {configuredProviders} configured
                </Badge>
              </div>
              <Separator />
              <div className="space-y-3">
                {['ollama', 'openai', 'gemini', 'stability', 'replicate'].map((providerKey) => {
                  const status = providerStatus[providerKey];
                  return (
                    <div key={providerKey} className="flex items-center justify-between">
                      <div>
                        <Label>{status?.label ?? providerKey}</Label>
                        <p className="text-xs text-muted-foreground">{status?.summary ?? 'Provider status unavailable'}</p>
                      </div>
                      <Badge variant={status?.configured ? 'default' : 'outline'}>
                        {status?.configured ? 'Configured' : 'Not configured'}
                      </Badge>
                    </div>
                  );
                })}
              </div>
              <Separator />
              <div className="text-xs text-muted-foreground">
                {isLoadingProviders ? 'Loading provider settings...' : `Provider config file: ${envPath || '.env'}`}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Autonomous Systems
              </CardTitle>
              <CardDescription>Configure self-healing and optimization</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Watchdog Interval</Label>
                  <span className="text-sm">{watchdogInterval[0]}s</span>
                </div>
                <Slider value={watchdogInterval} onValueChange={setWatchdogInterval} min={10} max={300} step={10} />
                <p className="text-xs text-muted-foreground">Health check frequency (10s - 5min)</p>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto Recovery</Label>
                  <p className="text-xs text-muted-foreground">Automatically fix issues</p>
                </div>
                <Switch checked={autoRecovery} onCheckedChange={setAutoRecovery} />
              </div>
              <Separator />
              <div className="space-y-2">
                <Label>Optimization Strategy</Label>
                <Select value={optimizationStrategy} onValueChange={setOptimizationStrategy}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="aggressive">Aggressive</SelectItem>
                    <SelectItem value="balanced">Balanced</SelectItem>
                    <SelectItem value="conservative">Conservative</SelectItem>
                    <SelectItem value="adaptive">Adaptive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Max Memory Usage</Label>
                  <span className="text-sm">{maxMemoryPercent[0]}%</span>
                </div>
                <Slider value={maxMemoryPercent} onValueChange={setMaxMemoryPercent} min={50} max={95} step={5} />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Provider Features</CardTitle>
          <CardDescription>
            These values are written to the backend `.env` file and applied to new provider clients immediately.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          {PROVIDER_GROUPS.map((group) => (
            <div key={group.title} className="space-y-4">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="font-semibold">{group.title}</h3>
                  <p className="text-sm text-muted-foreground">{group.description}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {group.providers.map((providerKey) => {
                    const status = providerStatus[providerKey];
                    return (
                      <Badge key={providerKey} variant={status?.configured ? 'default' : 'outline'}>
                        {status?.label ?? providerKey}
                      </Badge>
                    );
                  })}
                </div>
              </div>

              {group.title === 'Local & LLM Providers' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Ollama Base URL</Label>
                    <Input
                      value={providerSettings.ollama_base_url}
                      onChange={(e) => updateProviderField('ollama_base_url', e.target.value)}
                      placeholder="http://localhost:11434"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Ollama Model</Label>
                    <Input
                      value={providerSettings.ollama_model}
                      onChange={(e) => updateProviderField('ollama_model', e.target.value)}
                      placeholder="llama3"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>OpenAI API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.openai_api_key}
                      onChange={(e) => updateProviderField('openai_api_key', e.target.value)}
                      placeholder="sk-..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Google Gemini API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.google_gemini_api_key}
                      onChange={(e) => updateProviderField('google_gemini_api_key', e.target.value)}
                      placeholder="AIza..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Anthropic API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.anthropic_api_key}
                      onChange={(e) => updateProviderField('anthropic_api_key', e.target.value)}
                      placeholder="sk-ant-..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Hugging Face API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.huggingface_api_key}
                      onChange={(e) => updateProviderField('huggingface_api_key', e.target.value)}
                      placeholder="hf_..."
                    />
                  </div>
                </div>
              )}

              {group.title === 'Image & Vision Providers' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Stability API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.stability_api_key}
                      onChange={(e) => updateProviderField('stability_api_key', e.target.value)}
                      placeholder="sk-..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Replicate API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.replicate_api_key}
                      onChange={(e) => updateProviderField('replicate_api_key', e.target.value)}
                      placeholder="r8_..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>AWS Region</Label>
                    <Input
                      value={providerSettings.aws_region}
                      onChange={(e) => updateProviderField('aws_region', e.target.value)}
                      placeholder="us-east-1"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>AWS Access Key ID</Label>
                    <Input
                      type="password"
                      value={providerSettings.aws_access_key_id}
                      onChange={(e) => updateProviderField('aws_access_key_id', e.target.value)}
                      placeholder="AKIA..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>AWS Secret Access Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.aws_secret_access_key}
                      onChange={(e) => updateProviderField('aws_secret_access_key', e.target.value)}
                      placeholder="AWS secret key"
                    />
                  </div>
                </div>
              )}

              {group.title === 'Search & Intelligence Providers' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label>Tavily API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.tavily_api_key}
                      onChange={(e) => updateProviderField('tavily_api_key', e.target.value)}
                      placeholder="tvly-..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Serper API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.serper_api_key}
                      onChange={(e) => updateProviderField('serper_api_key', e.target.value)}
                      placeholder="serper key"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>News API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.news_api_key}
                      onChange={(e) => updateProviderField('news_api_key', e.target.value)}
                      placeholder="newsapi key"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>OpenWeatherMap API Key</Label>
                    <Input
                      type="password"
                      value={providerSettings.openweathermap_api_key}
                      onChange={(e) => updateProviderField('openweathermap_api_key', e.target.value)}
                      placeholder="weather key"
                    />
                  </div>
                </div>
              )}

              <Separator />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
          <CardDescription>About this JARVIS installation</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Version</p>
              <p className="text-lg font-semibold">3.0.0</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Phase</p>
              <p className="text-lg font-semibold">Phase 3</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Backend</p>
              <p className="text-lg font-semibold">FastAPI</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Frontend</p>
              <p className="text-lg font-semibold">Next.js 14</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
