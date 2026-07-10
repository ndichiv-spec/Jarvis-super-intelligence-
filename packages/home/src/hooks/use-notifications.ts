"use client";

import { useCallback } from "react";
import { useAppStore } from "@/stores/app-store";
import { api } from "@/lib/api";
import type { Notification } from "@/types";

export function useNotificationActions() {
  const { notifications, addNotification, markNotificationRead, markAllNotificationsRead } = useAppStore();

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await api.notifications.list();
      return data;
    } catch {
      return [];
    }
  }, []);

  const markRead = useCallback(
    async (id: string) => {
      markNotificationRead(id);
      try {
        await api.notifications.markRead(id);
      } catch {
        // silent
      }
    },
    [markNotificationRead],
  );

  const markAllRead = useCallback(async () => {
    markAllNotificationsRead();
    try {
      await api.notifications.markAllRead();
    } catch {
      // silent
    }
  }, [markAllNotificationsRead]);

  return { notifications, fetchNotifications, markRead, markAllRead, addNotification };
}
