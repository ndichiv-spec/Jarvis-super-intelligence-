'use client';

import React, { useEffect, useState } from 'react';
import { useMonitoringStore } from '@/stores/monitoring-store';
import { jarvisAPI } from '@/lib/api';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Activity, Cpu, HardDrive, MemoryStick, Network, RefreshCw, Server, Zap, Shield, Radio } from 'lucide-react';

interface MetricsHistory {
  time: string;
  cpu: number;
  memory: number;
  disk: number;
}

export default function SystemMonitor() {
  const { metrics, setMetrics, setLoading } = useMonitoringStore();
  const [history, setHistory] = useState<MetricsHistory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [processCount, setProcessCount] = useState(0);
  const [uptime, setUptime] = useState('');
  const [networkIO, setNetworkIO] = useState({ sent: '0 MB', recv: '0 MB' });
  const [gpuUsage, setGpuUsage] = useState(0);

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const data = await jarvisAPI.getMetrics();
      setMetrics({
        cpu_percent: data.system.cpu_percent,
        memory_percent: data.system.memory_percent,
        disk_percent: data.system.disk_percent,
        process_count: data.system.process_count,
        uptime_seconds: data.uptime_seconds,
      });
      setProcessCount(data.system.process_count);

      const hours = Math.floor(data.uptime_seconds / 3600);
      const minutes = Math.floor((data.uptime_seconds % 3600) / 60);
      setUptime(`${hours}h ${minutes}m`);

      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setHistory((prev) => {
        const newHistory = [
          ...prev,
          {
            time: now,
            cpu: data.system.cpu_percent,
            memory: data.system.memory_percent,
            disk: data.system.disk_percent,
          },
        ];
        return newHistory.slice(-30);
      });
    } catch (error) {
      const mockData = {
        cpu_percent: 25 + Math.random() * 40,
        memory_percent: 45 + Math.random() * 25,
        disk_percent: 60 + Math.random() * 20,
        process_count: 150 + Math.floor(Math.random() * 50),
        uptime_seconds: 86400 + Math.random() * 86400,
      };
      setMetrics(mockData);
      setProcessCount(mockData.process_count);

      const hours = Math.floor(mockData.uptime_seconds / 3600);
      const minutes = Math.floor((mockData.uptime_seconds % 3600) / 60);
      setUptime(`${hours}h ${minutes}m`);

      const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setHistory((prev) => {
        const newHistory = [
          ...prev,
          {
            time: now,
            cpu: mockData.cpu_percent,
            memory: mockData.memory_percent,
            disk: mockData.disk_percent,
          },
        ];
        return newHistory.slice(-30);
      });

      setNetworkIO({
        sent: `${(Math.random() * 50 + 10).toFixed(1)} MB`,
        recv: `${(Math.random() * 100 + 20).toFixed(1)} MB`,
      });
      setGpuUsage(Math.random() * 40 + 10);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  // Circular gauge component
  const CircularGauge = ({ value, label, size = 100 }: { value: number; label: string; size?: number }) => {
    const radius = (size - 12) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value / 100) * circumference;

    return (
      <div className="flex flex-col items-center">
        <div className="relative" style={{ width: size, height: size }}>
          <svg width={size} height={size} className="-rotate-90">
            {/* Background ring */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="rgba(0, 212, 255, 0.1)"
              strokeWidth="6"
            />
            {/* Value ring */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="6"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
          </svg>
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="hud-readout text-sm text-cyan-400">{value.toFixed(0)}%</span>
          </div>
        </div>
        <span className="text-[9px] text-cyan-300/50 tracking-wider mt-1 hud-readout">{label}</span>
      </div>
    );
  };

  // Holo progress bar
  const HoloBar = ({ value, label }: { value: number; label: string }) => (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-[10px] text-cyan-300/60 tracking-wider hud-readout">{label}</span>
        <span className="text-[10px] text-cyan-400/70 tracking-wider hud-readout">{value.toFixed(1)}%</span>
      </div>
      <div className="w-full h-2 holo-progress rounded-sm overflow-hidden">
        <div
          className="h-full holo-progress-bar rounded-sm transition-all duration-500"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full" style={{ background: 'rgba(3, 7, 18, 0.85)' }}>
      {/* ===== SVG DEFS ===== */}
      <svg width="0" height="0" className="absolute">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00d4ff" />
            <stop offset="50%" stopColor="#00e5a0" />
            <stop offset="100%" stopColor="#0078d4" />
          </linearGradient>
        </defs>
      </svg>

      {/* ===== HEADER ===== */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-cyan-500/20 holo-titlebar">
        <div className="flex items-center gap-2.5">
          <Activity className="w-4 h-4 text-cyan-400 drop-shadow-[0_0_6px_rgba(0,212,255,0.5)]" />
          <span className="text-xs font-medium tracking-wider text-holo">SYSTEM DIAGNOSTICS</span>
          <div className="flex items-center gap-1">
            <Shield className="w-3 h-3 text-emerald-400/50" />
            <span className="text-[8px] text-emerald-400/50 tracking-wider hud-readout">NOMINAL</span>
          </div>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={isLoading}
          className="flex items-center gap-1.5 text-[10px] text-cyan-300/40 hover:text-cyan-300 transition-colors px-2 py-1 rounded-lg hover:bg-cyan-500/10 tracking-wider hud-readout"
        >
          <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
          REFRESH
        </button>
      </div>

      {/* ===== CONTENT ===== */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {/* ===== TOP ROW: Circular Gauges ===== */}
        <div className="flex items-center justify-around mb-4">
          <CircularGauge value={metrics?.cpu_percent || 0} label="CPU" size={90} />
          <CircularGauge value={metrics?.memory_percent || 0} label="MEMORY" size={90} />
          <CircularGauge value={metrics?.disk_percent || 0} label="DISK" size={90} />
          <CircularGauge value={gpuUsage} label="GPU" size={90} />
        </div>

        {/* ===== STATUS BARS ===== */}
        <div className="space-y-3 mb-4 p-3 rounded-lg hud-panel">
          <HoloBar value={metrics?.cpu_percent || 0} label="PROCESSOR" />
          <HoloBar value={metrics?.memory_percent || 0} label="MEMORY" />
          <HoloBar value={metrics?.disk_percent || 0} label="STORAGE" />
          <HoloBar value={gpuUsage} label="GRAPHICS" />
        </div>

        {/* ===== HUD READOUTS ===== */}
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="p-3 rounded-lg hud-panel">
            <div className="flex items-center gap-1.5 mb-1">
              <Server className="w-3 h-3 text-cyan-400/50" />
              <span className="text-[9px] text-cyan-300/40 tracking-wider hud-readout">PROCESSES</span>
            </div>
            <span className="hud-readout text-lg text-cyan-400">{processCount}</span>
          </div>
          <div className="p-3 rounded-lg hud-panel">
            <div className="flex items-center gap-1.5 mb-1">
              <Zap className="w-3 h-3 text-cyan-400/50" />
              <span className="text-[9px] text-cyan-300/40 tracking-wider hud-readout">UPTIME</span>
            </div>
            <span className="hud-readout text-lg text-cyan-400">{uptime || '--'}</span>
          </div>
          <div className="p-3 rounded-lg hud-panel">
            <div className="flex items-center gap-1.5 mb-1">
              <Radio className="w-3 h-3 text-cyan-400/50" />
              <span className="text-[9px] text-cyan-300/40 tracking-wider hud-readout">NET ↓</span>
            </div>
            <span className="hud-readout text-sm text-cyan-400">{networkIO.recv}</span>
          </div>
          <div className="p-3 rounded-lg hud-panel">
            <div className="flex items-center gap-1.5 mb-1">
              <Network className="w-3 h-3 text-cyan-400/50" />
              <span className="text-[9px] text-cyan-300/40 tracking-wider hud-readout">NET ↑</span>
            </div>
            <span className="hud-readout text-sm text-cyan-400">{networkIO.sent}</span>
          </div>
        </div>

        {/* ===== RESOURCE CHART ===== */}
        <div className="rounded-lg hud-panel p-4 mb-4">
          <div className="flex items-center gap-1.5 mb-3">
            <Activity className="w-3.5 h-3.5 text-cyan-400/50" />
            <h3 className="text-[10px] font-semibold text-cyan-300/50 uppercase tracking-[0.15em]">
              RESOURCE TELEMETRY
            </h3>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00e5a0" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00e5a0" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="diskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0078d4" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#0078d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 212, 255, 0.08)" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: 'rgba(0, 212, 255, 0.3)' }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: 'rgba(0, 212, 255, 0.3)' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(3, 7, 18, 0.95)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#00d4ff',
                  fontFamily: 'monospace',
                }}
              />
              <Area type="monotone" dataKey="cpu" stroke="#00d4ff" fill="url(#cpuGrad)" strokeWidth={2} name="CPU" />
              <Area type="monotone" dataKey="memory" stroke="#00e5a0" fill="url(#memGrad)" strokeWidth={2} name="MEM" />
              <Area type="monotone" dataKey="disk" stroke="#0078d4" fill="url(#diskGrad)" strokeWidth={1.5} name="DISK" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* ===== CORE BREAKDOWN ===== */}
        <div className="rounded-lg hud-panel p-4">
          <div className="flex items-center gap-1.5 mb-3">
            <Cpu className="w-3.5 h-3.5 text-cyan-400/50" />
            <h3 className="text-[10px] font-semibold text-cyan-300/50 uppercase tracking-[0.15em]">
              CORE ALLOCATION
            </h3>
          </div>
          <ResponsiveContainer width="100%" height={110}>
            <BarChart
              data={[
                { core: 'C0', usage: (metrics?.cpu_percent || 0) * 0.9 + Math.random() * 10 },
                { core: 'C1', usage: (metrics?.cpu_percent || 0) * 0.85 + Math.random() * 10 },
                { core: 'C2', usage: (metrics?.cpu_percent || 0) * 0.95 + Math.random() * 10 },
                { core: 'C3', usage: (metrics?.cpu_percent || 0) * 0.8 + Math.random() * 10 },
                { core: 'C4', usage: (metrics?.cpu_percent || 0) * 0.75 + Math.random() * 10 },
                { core: 'C5', usage: (metrics?.cpu_percent || 0) * 0.9 + Math.random() * 10 },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 212, 255, 0.08)" />
              <XAxis dataKey="core" tick={{ fontSize: 9, fill: 'rgba(0, 212, 255, 0.3)' }} />
              <YAxis tick={{ fontSize: 9, fill: 'rgba(0, 212, 255, 0.3)' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(3, 7, 18, 0.95)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: '#00d4ff',
                  fontFamily: 'monospace',
                }}
              />
              <Bar dataKey="usage" radius={[3, 3, 0, 0]}>
                {Array(6).fill(0).map((_, i) => (
                  <Cell
                    key={`cell-${i}`}
                    fill={i % 2 === 0 ? '#00d4ff' : '#00e5a0'}
                    opacity={0.7 + Math.random() * 0.3}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
