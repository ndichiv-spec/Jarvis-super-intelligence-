from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jarvis_communication.models import ChannelType, NotificationLevel


class MetricsCollector:
    def __init__(self) -> None:
        self.messages_sent: int = 0
        self.messages_read: int = 0
        self.notifications_sent: int = 0
        self.streams_started: int = 0
        self.streams_ended: int = 0
        self.errors: int = 0
        self._channel_counts: dict[str, int] = {}
        self._notification_level_counts: dict[str, int] = {}
        self._latency_samples: list[float] = []
        self._start_time: datetime = datetime.now(UTC)

    def record_message_sent(self, channel: ChannelType) -> None:
        self.messages_sent += 1
        self._channel_counts[channel.value] = self._channel_counts.get(channel.value, 0) + 1

    def record_message_read(self) -> None:
        self.messages_read += 1

    def record_notification_sent(self, level: NotificationLevel) -> None:
        self.notifications_sent += 1
        self._notification_level_counts[level.value] = (
            self._notification_level_counts.get(level.value, 0) + 1
        )

    def record_stream_started(self) -> None:
        self.streams_started += 1

    def record_stream_ended(self) -> None:
        self.streams_ended += 1

    def record_error(self) -> None:
        self.errors += 1

    def record_latency(self, value_ms: float) -> None:
        self._latency_samples.append(value_ms)

    def get_channel_breakdown(self) -> dict[str, int]:
        return dict(self._channel_counts)

    def get_notification_breakdown(self) -> dict[str, int]:
        return dict(self._notification_level_counts)

    def get_latency_stats(self) -> dict[str, float]:
        if not self._latency_samples:
            return {"avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0, "count": 0}
        return {
            "avg_ms": sum(self._latency_samples) / len(self._latency_samples),
            "min_ms": min(self._latency_samples),
            "max_ms": max(self._latency_samples),
            "count": len(self._latency_samples),
        }

    def get_uptime(self) -> timedelta:
        return datetime.now(UTC) - self._start_time

    def get_all_metrics(self) -> dict[str, Any]:
        return {
            "messages_sent": self.messages_sent,
            "messages_read": self.messages_read,
            "notifications_sent": self.notifications_sent,
            "streams_started": self.streams_started,
            "streams_ended": self.streams_ended,
            "errors": self.errors,
            "channel_breakdown": self.get_channel_breakdown(),
            "notification_breakdown": self.get_notification_breakdown(),
            "latency": self.get_latency_stats(),
            "uptime_seconds": self.get_uptime().total_seconds(),
        }

    def reset(self) -> None:
        self.messages_sent = 0
        self.messages_read = 0
        self.notifications_sent = 0
        self.streams_started = 0
        self.streams_ended = 0
        self.errors = 0
        self._channel_counts.clear()
        self._notification_level_counts.clear()
        self._latency_samples.clear()
        self._start_time = datetime.now(UTC)
