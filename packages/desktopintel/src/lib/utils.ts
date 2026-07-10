import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatRelativeTime(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}

export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (mins > 0) parts.push(`${mins}m`);
  return parts.join(" ") || "<1m";
}

export function getPermissionLabel(permission: string): string {
  const labels: Record<string, string> = {
    "file:read": "Read Files",
    "file:write": "Write Files",
    "folder:select": "Select Folders",
    "clipboard:read": "Read Clipboard",
    "clipboard:write": "Write Clipboard",
    "notification:send": "Send Notifications",
    "camera:access": "Camera Access",
    "microphone:access": "Microphone Access",
    "screen:capture": "Screen Capture",
    "integration:launch": "Launch Integrations",
    "network:connect": "Network Connect",
    "device:info": "Device Information",
  };
  return labels[permission] || permission;
}

export function getPermissionDescription(permission: string): string {
  const descriptions: Record<string, string> = {
    "file:read": "Read files from selected locations",
    "file:write": "Write and save files to selected locations",
    "folder:select": "Select folders for file operations",
    "clipboard:read": "Read content from your clipboard",
    "clipboard:write": "Copy content to your clipboard",
    "notification:send": "Display desktop notifications",
    "camera:access": "Access your camera for capture",
    "microphone:access": "Access your microphone for recording",
    "screen:capture": "Capture your screen content",
    "integration:launch": "Launch and interact with local applications",
    "network:connect": "Connect to network services",
    "device:info": "Access device information",
  };
  return descriptions[permission] || permission;
}
