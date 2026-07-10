"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { ErrorState } from "@/components/shared/error-state";
import { MessageSquare, Bell, Users, Radio, Mail, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ConversationSummary {
  conversation_id: string;
  title: string;
  participants: string[];
  message_count: number;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

interface NotificationSummary {
  notification_id: string;
  title: string;
  body: string;
  level: string;
  source: string;
  read: boolean;
  timestamp: string;
}

interface PresenceSummary {
  user_id: string;
  status: string;
  current_activity: string;
  last_seen: string | null;
  connected_clients: number;
}

interface MetricsSummary {
  messages_sent: number;
  notifications_sent: number;
  active_sessions: number;
  active_presence: number;
  conversation_count: number;
}

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${GATEWAY_URL}/gateway${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const body = await res.json();
  if (!body.ok) throw new Error(body.error?.message || "API error");
  return body.data as T;
}

export default function CommunicationPage() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [recentConversations, setRecentConversations] = useState<ConversationSummary[]>([]);
  const [recentNotifications, setRecentNotifications] = useState<NotificationSummary[]>([]);
  const [presence, setPresence] = useState<PresenceSummary[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [metricsData, convsData, notifsData, presenceData] = await Promise.all([
          fetchApi<MetricsSummary>("/communication/metrics"),
          fetchApi<ConversationSummary[]>("/communication/conversations"),
          fetchApi<NotificationSummary[]>(`/communication/notifications?user_id=system`),
          fetchApi<PresenceSummary[]>("/communication/presence"),
        ]);
        setMetrics(metricsData);
        setRecentConversations(convsData.slice(0, 5));
        setRecentNotifications(notifsData.slice(0, 5));
        setPresence(presenceData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load communication data");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Communication Dashboard"
        description="Monitor and manage JARVIS communication platform"
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Messages Sent"
          value={metrics?.messages_sent ?? 0}
          icon={MessageSquare}
          description="Total messages delivered"
        />
        <StatCard
          title="Notifications"
          value={metrics?.notifications_sent ?? 0}
          icon={Bell}
          description="Notifications dispatched"
        />
        <StatCard
          title="Active Users"
          value={metrics?.active_presence ?? 0}
          icon={Users}
          description="Currently online"
        />
        <StatCard
          title="Active Streams"
          value={0}
          icon={Radio}
          description="Live data streams"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <MessageSquare className="h-5 w-5" />
              Recent Conversations
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentConversations.length === 0 ? (
              <p className="text-sm text-muted-foreground">No conversations yet.</p>
            ) : (
              <div className="space-y-3">
                {recentConversations.map((conv) => (
                  <div key={conv.conversation_id} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{conv.title || "Untitled"}</p>
                      <p className="text-xs text-muted-foreground">
                        {conv.participants.length} participants &middot; {conv.message_count} messages
                      </p>
                    </div>
                    <Badge variant={conv.is_archived ? "secondary" : "default"}>
                      {conv.is_archived ? "Archived" : "Active"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Bell className="h-5 w-5" />
              Recent Notifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentNotifications.length === 0 ? (
              <p className="text-sm text-muted-foreground">No notifications yet.</p>
            ) : (
              <div className="space-y-3">
                {recentNotifications.map((notif) => (
                  <div key={notif.notification_id} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{notif.title}</p>
                      <p className="truncate text-xs text-muted-foreground">{notif.body}</p>
                    </div>
                    <Badge
                      variant={
                        notif.level === "error" || notif.level === "critical"
                          ? "destructive"
                          : notif.level === "warning"
                          ? "secondary"
                          : "default"
                      }
                    >
                      {notif.level}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Users className="h-5 w-5" />
            Active Presence
          </CardTitle>
        </CardHeader>
        <CardContent>
          {presence.length === 0 ? (
            <p className="text-sm text-muted-foreground">No users online.</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {presence.map((p) => (
                <div key={p.user_id} className="flex items-center gap-3 rounded-lg border p-3">
                  <div
                    className={`h-3 w-3 rounded-full ${
                      p.status === "online" ? "bg-green-500" :
                      p.status === "busy" ? "bg-yellow-500" :
                      p.status === "away" ? "bg-orange-400" :
                      "bg-gray-400"
                    }`}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{p.user_id}</p>
                    <p className="text-xs text-muted-foreground">{p.current_activity || p.status}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
