from __future__ import annotations

import pytest

from jarvis_communication.templates import TemplateEngine


@pytest.fixture
def engine() -> TemplateEngine:
    eng = TemplateEngine()
    eng.register("greeting", "Hello, {name}!")
    eng.register_email_template("welcome", "Welcome {user}", "Hi {user}, welcome to JARVIS!")
    eng.register_notification_template("alert", "Alert: {title}", "{message}")
    return eng


def test_render(engine: TemplateEngine) -> None:
    result = engine.render("greeting", name="World")
    assert result == "Hello, World!"


def test_render_missing_template(engine: TemplateEngine) -> None:
    with pytest.raises(ValueError, match="not found"):
        engine.render("nonexistent")


def test_register_unregister(engine: TemplateEngine) -> None:
    engine.register("temp", "Template {x}")
    assert "temp" in engine.list_templates()
    engine.unregister("temp")
    assert "temp" not in engine.list_templates()


def test_render_email(engine: TemplateEngine) -> None:
    result = engine.render_email("welcome", user="Alice")
    assert result["subject"] == "Welcome Alice"
    assert "Alice" in result["body"]


def test_render_notification(engine: TemplateEngine) -> None:
    result = engine.render_notification("alert", title="Server Down", message="Server is down")
    assert result["title"] == "Alert: Server Down"
    assert result["body"] == "Server is down"


def test_render_report(engine: TemplateEngine) -> None:
    engine.register_report_template("summary", "Report: {period}")
    result = engine.render_report("summary", period="Q1")
    assert result == "Report: Q1"


def test_render_system_message(engine: TemplateEngine) -> None:
    engine.register_system_template("shutdown", "System shutting down: {reason}")
    result = engine.render_system_message("shutdown", reason="Maintenance")
    assert result == "System shutting down: Maintenance"


def test_render_agent_message(engine: TemplateEngine) -> None:
    engine.register_agent_template("status", "Agent {name}: {status}")
    result = engine.render_agent_message("status", name="VisionAgent", status="running")
    assert result == "Agent VisionAgent: running"


def test_render_meeting_summary(engine: TemplateEngine) -> None:
    engine.register_meeting_summary_template("daily", "Meeting: {title} - {attendees}")
    result = engine.render_meeting_summary("daily", title="Standup", attendees="5")
    assert result == "Meeting: Standup - 5"
