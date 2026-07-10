export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  publisher: string;
  icon?: string;
}

export interface PluginContribution {
  sidebarItems?: { href: string; label: string; icon: string; section: string }[];
  commands?: { id: string; label: string; category: string; action: () => void }[];
  toolbarActions?: { id: string; label: string; icon: string; action: () => void }[];
  settingsTabs?: { id: string; label: string; component: string }[];
}

export interface Plugin {
  manifest: PluginManifest;
  contributions: PluginContribution;
  onActivate?: () => void | Promise<void>;
  onDeactivate?: () => void | Promise<void>;
}

class PluginRegistry {
  private plugins = new Map<string, Plugin>();

  register(plugin: Plugin): void {
    this.plugins.set(plugin.manifest.id, plugin);
  }

  unregister(id: string): void {
    this.plugins.delete(id);
  }

  get(id: string): Plugin | undefined {
    return this.plugins.get(id);
  }

  list(): Plugin[] {
    return Array.from(this.plugins.values());
  }

  getContributions(): PluginContribution {
    const combined: PluginContribution = {};
    for (const plugin of this.plugins.values()) {
      if (plugin.contributions.sidebarItems) {
        combined.sidebarItems = [...(combined.sidebarItems || []), ...plugin.contributions.sidebarItems];
      }
      if (plugin.contributions.commands) {
        combined.commands = [...(combined.commands || []), ...plugin.contributions.commands];
      }
      if (plugin.contributions.toolbarActions) {
        combined.toolbarActions = [...(combined.toolbarActions || []), ...plugin.contributions.toolbarActions];
      }
      if (plugin.contributions.settingsTabs) {
        combined.settingsTabs = [...(combined.settingsTabs || []), ...plugin.contributions.settingsTabs];
      }
    }
    return combined;
  }

  async activateAll(): Promise<void> {
    for (const plugin of this.plugins.values()) {
      await plugin.onActivate?.();
    }
  }

  async deactivateAll(): Promise<void> {
    for (const plugin of this.plugins.values()) {
      await plugin.onDeactivate?.();
    }
  }
}

export const pluginRegistry = new PluginRegistry();
