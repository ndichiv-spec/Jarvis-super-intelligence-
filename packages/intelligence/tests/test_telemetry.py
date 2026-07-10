from dataclasses import dataclass
from datetime import UTC, datetime
from jarvis_intelligence.telemetry import TelemetryEngine, TelemetryEvent, ExecutionMetrics


@dataclass
class FakeReport:
    total_tasks: int = 5
    completed_tasks: int = 4
    failed_tasks: int = 1
    duration_seconds: float = 12.5
    decisions_made: int = 6


class TestTelemetryEngine:
    def test_record_execution(self):
        engine = TelemetryEngine()
        report = FakeReport()
        engine.record_execution("plan-1", report)
        metrics = engine.get_metrics("plan-1")
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 0
        assert metrics.failed_executions == 1
        assert metrics.tasks_completed == 4
        assert metrics.tasks_failed == 1
        assert metrics.last_execution_time is not None

    def test_record_execution_success(self):
        engine = TelemetryEngine()
        report = FakeReport(completed_tasks=5, failed_tasks=0)
        engine.record_execution("plan-2", report)
        metrics = engine.get_metrics("plan-2")
        assert metrics.successful_executions == 1
        assert metrics.failed_executions == 0

    def test_global_metrics(self):
        engine = TelemetryEngine()
        engine.record_execution("plan-1", FakeReport())
        engine.record_execution("plan-2", FakeReport())
        global_metrics = engine.get_metrics()
        assert global_metrics.total_executions == 2
        assert global_metrics.tasks_completed == 8

    def test_get_metrics_nonexistent(self):
        engine = TelemetryEngine()
        metrics = engine.get_metrics("nonexistent")
        assert metrics.total_executions == 0

    def test_record_event(self):
        engine = TelemetryEngine()
        engine.record_event("goal_created", "plan-1", {"description": "Test"})
        events = engine.get_events()
        assert len(events) == 1
        assert events[0].event_type == "goal_created"
        assert events[0].plan_id == "plan-1"

    def test_get_events_limit(self):
        engine = TelemetryEngine()
        for i in range(5):
            engine.record_event(f"event_{i}", "plan-1")
        events = engine.get_events(limit=2)
        assert len(events) == 2

    def test_events_ordered_by_timestamp_desc(self):
        engine = TelemetryEngine()
        engine.record_event("first", "p1")
        engine.record_event("second", "p1")
        events = engine.get_events()
        assert events[0].event_type == "second"

    def test_execution_metrics_defaults(self):
        metrics = ExecutionMetrics()
        assert metrics.total_executions == 0
        assert metrics.avg_duration_seconds == 0.0
        assert metrics.agents_used == []

    def test_telemetry_event_dataclass(self):
        now = datetime.now(UTC)
        event = TelemetryEvent(
            event_type="test", plan_id="p1",
            timestamp=now, data={"key": "value"},
        )
        assert event.event_type == "test"
        assert event.data["key"] == "value"
