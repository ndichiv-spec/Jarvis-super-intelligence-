'use client';

import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  MessageSquare, Activity, Bot, Library, Volume2, Settings,
  Shield, Code2, BookOpen, MonitorPlay,
} from 'lucide-react';

interface QuickAction {
  label: string;
  href: string;
  icon: React.ElementType;
  description: string;
  color: string;
}

const ACTIONS: QuickAction[] = [
  { label: 'Chat', href: '/dashboard', icon: MessageSquare, description: 'Neural conversation', color: 'from-blue-500 to-cyan-400' },
  { label: 'Monitoring', href: '/dashboard/monitoring', icon: Activity, description: 'System health', color: 'from-emerald-500 to-teal-400' },
  { label: 'Agents', href: '/dashboard/agents', icon: Bot, description: 'Task orchestration', color: 'from-purple-500 to-pink-400' },
  { label: 'Memory', href: '/dashboard/memory', icon: Library, description: 'Knowledge recall', color: 'from-amber-500 to-orange-400' },
  { label: 'Voice', href: '/voice', icon: Volume2, description: 'Speech interface', color: 'from-rose-500 to-red-400' },
  { label: 'Knowledge', href: '/dashboard/knowledge', icon: BookOpen, description: 'Information base', color: 'from-indigo-500 to-violet-400' },
  { label: 'Desktop', href: '/desktop', icon: MonitorPlay, description: 'Remote control', color: 'from-sky-500 to-blue-400' },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings, description: 'Configuration', color: 'from-gray-500 to-slate-400' },
];

export function QuickActions() {
  const router = useRouter();

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {ACTIONS.map((action) => {
        const Icon = action.icon;
        return (
          <motion.button
            key={action.href}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push(action.href)}
            className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/[0.02] p-3 text-left transition-all hover:border-white/20 hover:bg-white/[0.04]"
          >
            <div className={`mb-2 inline-flex rounded-lg bg-gradient-to-br ${action.color} p-2 shadow-lg`}>
              <Icon className="h-4 w-4 text-white" />
            </div>
            <p className="text-sm font-medium text-foreground/80">{action.label}</p>
            <p className="text-[10px] text-muted-foreground/40">{action.description}</p>
          </motion.button>
        );
      })}
    </div>
  );
}
