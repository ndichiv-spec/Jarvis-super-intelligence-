import { type Plugin, pluginRegistry } from "@/lib/plugin-sdk";

const gitPlugin: Plugin = {
  manifest: {
    id: "jarvis.git-integration",
    name: "Git Integration",
    version: "1.0.0",
    description: "Version control integration for JARVIS Studio",
    publisher: "JARVIS Labs",
  },
  contributions: {
    commands: [
      { id: "git.commit", label: "Commit Changes", category: "Git", action: () => {} },
      { id: "git.push", label: "Push to Remote", category: "Git", action: () => {} },
      { id: "git.pull", label: "Pull from Remote", category: "Git", action: () => {} },
    ],
    toolbarActions: [
      { id: "git.status", label: "Git Status", icon: "GitBranch", action: () => {} },
    ],
  },
  onActivate: async () => {
    console.log("Git Integration plugin activated");
  },
  onDeactivate: async () => {
    console.log("Git Integration plugin deactivated");
  },
};

pluginRegistry.register(gitPlugin);
export default gitPlugin;
