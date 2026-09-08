'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChatWindow } from '@/components/chat/chat-window';
import { DashboardWidgets } from '@/components/dashboard/dashboard-widgets';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { VoiceInterface } from '@/components/voice/voice-interface';
import { AgentActivity } from '@/components/agents/agent-activity';
import { MemoryInspector } from '@/components/memory/memory-inspector';
import { AutomationMonitor } from '@/components/automation/automation-monitor';
import FileStructureDisplay from '@/components/FileStructureDisplay';

type Tab = 'chat' | 'agents' | 'memory' | 'voice' | 'automation' | 'structure';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      {/* Metrics Strip */}
      <div className="shrink-0 p-4 pb-0">
        <DashboardWidgets />
      </div>

      {/* Quick Actions & Tab Navigation */}
      <div className="shrink-0 p-4 pb-0">
        <QuickActions />
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center gap-1 border-b border-white/5 px-4 pt-4">
        {[
          { id: 'chat' as const, label: 'Chat' },
          { id: 'agents' as const, label: 'Agents' },
          { id: 'memory' as const, label: 'Memory' },
          { id: 'voice' as const, label: 'Voice' },
          { id: 'automation' as const, label: 'Automation' },
          { id: 'structure' as const, label: 'Structure' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`relative px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'text-blue-400'
                : 'text-muted-foreground/50 hover:text-foreground'
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-400"
              />
            )}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="h-full"
        >
          {activeTab === 'chat' && <ChatWindow showSidebar={false} />}
          {activeTab === 'agents' && (
            <div className="h-full overflow-y-auto p-4">
              <AgentActivity />
            </div>
          )}
          {activeTab === 'memory' && (
            <div className="h-full overflow-y-auto p-4">
              <MemoryInspector />
            </div>
          )}
          {activeTab === 'voice' && (
            <div className="h-full overflow-y-auto p-4">
              <VoiceInterface />
            </div>
          )}
          {activeTab === 'automation' && (
            <div className="h-full overflow-y-auto p-4">
              <AutomationMonitor />
            </div>
          )}
          {activeTab === 'structure' && (
            <div className="h-full overflow-y-auto">
              <FileStructureDisplay />
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
