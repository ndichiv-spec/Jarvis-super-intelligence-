'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Brain, Bot, Cpu, Activity, BookOpen, Settings, Shield,
  Layers, MessageSquare, Workflow, MonitorPlay, Code2,
  ArrowUpCircle, Library, Server, Globe, Zap,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChatStore } from '@/features/chat/store';
import { useMonitoringStore } from '@/features/monitoring/store';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
  category: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Neural Chat', href: '/dashboard', icon: Brain, category: 'AI Core' },
  { label: 'Agent Orchestration', href: '/dashboard/agents', icon: Bot, category: 'AI Core' },
  { label: 'OMEGA Control', href: '/omega', icon: Layers, badge: 'OMEGA', category: 'AI Core' },
  { label: 'Virtual Desktop', href: '/desktop', icon: MonitorPlay, badge: 'NEW', category: 'Workspace' },
  { label: 'Workflows', href: '/workflows', icon: Workflow, category: 'Workspace' },
  { label: 'Voice Interface', href: '/voice', icon: Globe, badge: 'BETA', category: 'AI Core' },
  { label: 'System Control', href: '/dashboard/system', icon: Cpu, category: 'Infrastructure' },
  { label: 'Knowledge Matrix', href: '/dashboard/knowledge', icon: BookOpen, category: 'Infrastructure' },
  { label: 'Command Center', href: '/dashboard/monitoring', icon: Activity, badge: 'LIVE', category: 'Infrastructure' },
  { label: 'Memory Inspector', href: '/dashboard/memory', icon: Library, category: 'Infrastructure' },
  { label: 'Self-Upgrade', href: '/upgrade', icon: ArrowUpCircle, category: 'System' },
  { label: 'Self-Reliant IDE', href: '/dashboard/self-reliant', icon: Code2, badge: 'NEW', category: 'System' },
  { label: 'Knowledge Hub', href: '/knowledge-hub', icon: Library, category: 'System' },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings, category: 'System' },
  { label: 'Admin Console', href: '/dashboard/admin', icon: Shield, badge: 'ENT', category: 'Enterprise' },
];

const SIDEBAR_WIDTH = 280;

interface SidebarProps {
  isMobile: boolean;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isMobile, isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const connected = useChatStore((s) => s.connected);
  const healthRate = useMonitoringStore((s) => s.health?.status === 'healthy' ? 98.5 : 85);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname?.startsWith(href) ?? false;
  };

  const groupedItems = NAV_ITEMS.reduce<Record<string, NavItem[]>>((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {});

  return (
    <>
      {isMobile && isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen flex-col border-r border-white/5 bg-gradient-to-b from-[hsl(222,47%,8%)] to-[hsl(222,47%,4%)] transition-all duration-300 ${
          isMobile && !isOpen ? '-translate-x-full' : 'translate-x-0'
        }`}
        style={{ width: SIDEBAR_WIDTH }}
      >
        <div className="flex h-16 items-center gap-3 border-b border-white/5 px-5">
          <div className="relative">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-lg shadow-blue-500/20">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="absolute -right-0.5 -top-0.5 flex h-3 w-3">
              {connected && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              )}
              <span className={`relative inline-flex h-3 w-3 rounded-full border-2 border-[hsl(222,47%,8%)] ${connected ? 'bg-emerald-500' : 'bg-gray-500'}`} />
            </span>
          </div>
          <div>
            <span className="text-lg font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
              JARVIS
            </span>
            <span className="ml-1.5 text-[10px] font-medium text-muted-foreground/60">v3.0</span>
          </div>
        </div>

        <ScrollArea className="flex-1 px-3 py-4">
          <nav className="space-y-5">
            {Object.entries(groupedItems).map(([category, items]) => (
              <div key={category}>
                <div className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/40">
                  {category}
                </div>
                <div className="space-y-1">
                  {items.map((item) => {
                    const active = isActive(item.href);
                    const Icon = item.icon;
                    return (
                      <Link key={item.href} href={item.href} onClick={isMobile ? onClose : undefined}>
                        <motion.div
                          whileHover={{ x: 4 }}
                          className={`relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                            active
                              ? 'bg-gradient-to-r from-blue-500/15 to-cyan-500/10 text-blue-400 border border-blue-500/20'
                              : 'text-muted-foreground/70 hover:bg-white/5 hover:text-foreground'
                          }`}
                        >
                          {active && (
                            <motion.div
                              layoutId="activeNav"
                              className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-1 rounded-r-full bg-gradient-to-b from-blue-400 to-cyan-400"
                            />
                          )}
                          <Icon className={`h-5 w-5 shrink-0 ${active ? 'text-blue-400' : 'text-muted-foreground/50'}`} />
                          <span className="flex-1">{item.label}</span>
                          {item.badge && (
                            <Badge className={`h-4 px-1.5 text-[9px] font-bold ${
                              item.badge === 'LIVE'
                                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                                : 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                            }`}>
                              {item.badge}
                            </Badge>
                          )}
                        </motion.div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>
        </ScrollArea>

        <div className="border-t border-white/5 p-4">
          <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3">
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="h-3.5 w-3.5 text-amber-400" />
                <span className="text-[11px] font-medium text-muted-foreground/60">System Status</span>
              </div>
              <span className="text-xs font-bold text-emerald-400">{healthRate}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-1000"
                style={{ width: `${healthRate}%` }}
              />
            </div>
            <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground/40">
              <span>Self-Healing: Active</span>
              <span>Phase 3</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
