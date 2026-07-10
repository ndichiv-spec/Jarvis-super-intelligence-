from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_automation.models import ScheduleDefinition, ScheduleType


@dataclass(slots=True)
class InMemorySchedulerEngine:
    _schedules: dict[str, ScheduleDefinition] = field(default_factory=dict)

    def register_schedule(self, schedule: ScheduleDefinition) -> None:
        self._schedules[schedule.schedule_id] = schedule

    def unregister_schedule(self, schedule_id: str) -> None:
        self._schedules.pop(schedule_id, None)

    def get_schedule(self, schedule_id: str) -> ScheduleDefinition | None:
        return self._schedules.get(schedule_id)

    def list_schedules(self) -> tuple[ScheduleDefinition, ...]:
        return tuple(self._schedules.values())

    def list_due(self) -> tuple[ScheduleDefinition, ...]:
        now = datetime.now(UTC)
        due: list[ScheduleDefinition] = []
        for schedule in self._schedules.values():
            if not schedule.enabled:
                continue
            if schedule.schedule_type == ScheduleType.ONE_TIME:
                if schedule.start_at is not None and schedule.start_at <= now:
                    due.append(schedule)
            elif schedule.schedule_type == ScheduleType.INTERVAL:
                due.append(schedule)
            elif schedule.schedule_type == ScheduleType.RECURRING:
                due.append(schedule)
            elif schedule.schedule_type == ScheduleType.CRON:
                due.append(schedule)
            elif schedule.schedule_type == ScheduleType.CALENDAR:
                if schedule.start_at is not None and schedule.start_at <= now:
                    due.append(schedule)
            elif schedule.schedule_type == ScheduleType.DELAY:
                due.append(schedule)
        return tuple(due)
