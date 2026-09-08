'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Activity, CheckCircle, XCircle, AlertTriangle, RefreshCw,
  TrendingUp, Zap, Clock, Shield, Server
} from 'lucide-react';
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { jarvisAPI, HealthReport, MetricsData } from '@/lib/api';
import { useMonitoringStore } from '@/stores/monitoring-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { formatDistanceToNow, format } from 'date-fns';

// Mock time-series data for charts
const generateMockTimeData = (points: number, base: number, variance: number) => {
  const data = [];
  const now = new Date();
  for (let i = points; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60000);
    data.push({
      time: format(time, 'HH:mm'),
      value: base + Math.random() * variance - variance / 2,
      p95: base + variance + Math.random() * 10,
      p50: base + Math.random() * variance / 2,
      requests: Math.floor(50 + Math.random() * 150),
    });
  }
  return data;
};

export default function MonitoringPage() {
  const { healthStatus, healthRate, metrics, recoveryHistory, optimizationReport, lastUpdated, isLoading, setLoading, setHealthStatus, setMetrics, setRecoveryHistory, setOptimizationReport, setLastUpdated } = useMonitoringStore();
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [timeData] = useState(() => generateMockTimeData(30, 45, 30));
  const [isRunning, setIsRunning] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [report, metricsData, recovery, optReport] = await Promise.all([
        jarvisAPI.getHealthReport().catch(() => null),
        jarvisAPI.getMetrics().catch(() => null),
        jarvisAPI.getRecoveryHistory().catch(() => []),
        jarvisAPI.getOptimizationReport().catch(() => null),
      ]);

      if (report) {
        setHealthReport(report);
        setHealthStatus(report.current_status, report.health_rate_percent);
      }
      if (metricsData) {
        setMetrics({
          ...metricsData.system,
          uptime_seconds: metricsData.uptime_seconds || 0,
        });
      }
      setRecoveryHistory(recovery || []);
      if (optReport) setOptimizationReport(optReport);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch monitoring data:', error);
    } finally {
      setLoading(false);
    }
  }, [setLoading, setHealthStatus, setMetrics, setRecoveryHistory, setOptimizationReport, setLastUpdated]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRunOptimization = async () => {
    setIsRunning(true);
    try {
      await jarvisAPI.triggerOptimization();
      toast.success('Optimization cycle completed');
      fetchData();
    } catch (error: any) {
      toast.error(`Optimization failed: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy': return <XCircle className="h-4 w-4 text-orange-500" />;
      case 'critical': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'low': return 'bg-gray-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="flex-1 space-y-6 p-6 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-8 w-8 text-blue-500" />
            Monitoring Dashboard
          </h1>
          <p className="text-muted-foreground">System health, performance metrics, and autonomous recovery</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {lastUpdated && (
            <span className="text-xs text-muted-foreground">
              Updated {formatDistanceToNow(lastUpdated)} ago
            </span>
          )}
        </div>
      </div>

      {/* Health Status Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="border-2">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="flex items-center gap-4">
                <div className={`w-4 h-4 rounded-full ${getStatusColor(healthStatus)} animate-pulse`} />
                <div>
                  <p className="text-sm text-muted-foreground">Overall Status</p>
                  <p className="text-2xl font-bold capitalize">{healthStatus}</p>
                </div>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Health Rate</p>
                <p className="text-4xl font-bold text-blue-500">{healthRate}%</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Avg Response Time</p>
                <p className="text-2xl font-bold">{healthReport?.avg_api_response_time_ms?.toFixed(0) || '0'}ms</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Total Checks</p>
                <p className="text-2xl font-bold">{healthReport?.total_checks || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* System Health Checks */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {healthReport?.latest_checks?.map((check, idx) => (
          <motion.div key={check.name} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: idx * 0.05 }}>
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium capitalize flex items-center gap-2">
                    {getStatusIcon(check.status)}
                    {check.name}
                  </CardTitle>
                  <Badge variant={check.status === 'healthy' ? 'default' : 'destructive'} className="text-xs">
                    {check.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground mb-2">{check.message}</p>
                {check.response_time_ms > 0 && (
                  <p className="text-xs text-muted-foreground">Response: {check.response_time_ms.toFixed(1)}ms</p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><TrendingUp className="h-5 w-5" />CPU Usage</CardTitle>
            <CardDescription>CPU utilization over last 30 minutes</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={timeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Zap className="h-5 w-5" />Response Time</CardTitle>
            <CardDescription>P95 and P50 latency over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={timeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                <Legend />
                <Line type="monotone" dataKey="p95" stroke="hsl(var(--destructive))" strokeWidth={2} name="P95" />
                <Line type="monotone" dataKey="p50" stroke="hsl(var(--primary))" strokeWidth={2} name="P50" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Server className="h-5 w-5" />Request Rate</CardTitle>
            <CardDescription>Requests per minute</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={timeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                <Bar dataKey="requests" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5" />System Metrics</CardTitle>
            <CardDescription>Current resource usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {metrics && (
              <>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">CPU</span>
                    <span className="text-sm font-medium">{metrics.cpu_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={metrics.cpu_percent} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Memory</span>
                    <span className="text-sm font-medium">{metrics.memory_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={metrics.memory_percent} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Disk</span>
                    <span className="text-sm font-medium">{metrics.disk_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={metrics.disk_percent} className="h-2" />
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recovery History & Optimization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recovery History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Clock className="h-5 w-5" />Recovery History</CardTitle>
            <CardDescription>Recent automated recovery actions</CardDescription>
          </CardHeader>
          <CardContent>
            {recoveryHistory.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
                <p>No recovery actions needed - system is healthy!</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {recoveryHistory.slice(0, 10).map((recovery: any, idx: number) => (
                  <div key={idx} className="p-3 bg-muted rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <Badge className={getSeverityColor(recovery.severity)}>{recovery.severity}</Badge>
                      <Badge variant={recovery.status === 'completed' ? 'default' : 'destructive'}>
                        {recovery.status}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium mt-2">{recovery.issue_description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {recovery.completed_at ? format(new Date(recovery.completed_at), 'MMM d, HH:mm') : 'Pending'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Optimization Report */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Zap className="h-5 w-5" />Optimization Report</CardTitle>
            <CardDescription>Self-optimization status and recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            {optimizationReport ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Current Profile</p>
                    <p className="text-lg font-semibold capitalize">{optimizationReport.current_profile || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Strategy</p>
                    <p className="text-lg font-semibold capitalize">{optimizationReport.strategy || 'N/A'}</p>
                  </div>
                </div>
                {optimizationReport.recommendations?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Recommendations:</p>
                    <ul className="space-y-2">
                      {optimizationReport.recommendations.map((rec: any, idx: number) => (
                        <li key={idx} className="text-sm flex items-start gap-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 shrink-0" />
                          <span>{rec.reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <Button onClick={handleRunOptimization} disabled={isRunning} className="w-full">
                  {isRunning ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Zap className="h-4 w-4 mr-2" />}
                  Run Optimization
                </Button>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p>No optimization data available</p>
                <Button onClick={handleRunOptimization} disabled={isRunning} className="mt-4">
                  <Zap className="h-4 w-4 mr-2" />
                  Run Optimization Now
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
