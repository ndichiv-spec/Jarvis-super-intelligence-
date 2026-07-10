from __future__ import annotations

from jarvis_brain.intent_engine import RuleBasedIntentEngine
from jarvis_brain.models import Capability, IntentKind, RawBrainRequest
from jarvis_brain.request_processor import DefaultRequestProcessor


def test_intent_engine_detects_tool_workflow() -> None:
    processor = DefaultRequestProcessor()
    request = processor.process(
        RawBrainRequest.create(
            "Run deployment tool for release",
            system_state={"mode": "normal"},
        )
    )

    intent = RuleBasedIntentEngine().determine_intent(request, request.context)

    assert intent.kind == IntentKind.TOOL_WORKFLOW
    assert Capability.TOOL_COORDINATION in intent.required_capabilities
    assert intent.ambiguous is False


def test_intent_engine_marks_ambiguous_and_missing_referent() -> None:
    processor = DefaultRequestProcessor()
    request = processor.process(
        RawBrainRequest.create("Research it and run tools for it ???")
    )

    intent = RuleBasedIntentEngine().determine_intent(request, request.context)

    assert intent.ambiguous is True
    assert "focused_question" in intent.missing_information
    assert "referent" in intent.missing_information
    assert Capability.CLARIFICATION in intent.required_capabilities
