from __future__ import annotations

import pytest
from jarvis_brain.models import RawBrainRequest


@pytest.fixture
def raw_request() -> RawBrainRequest:
    return RawBrainRequest.create(
        "Research deployment risks and run tool checks",
        conversation_context={"thread": "alpha"},
        user_context={"user_id": "u-1", "role": "developer"},
        memory_references=("mem-1",),
        knowledge_references=("kb-1",),
        workspace_context={"repo": "jarvis"},
        active_projects=("jarvis-core",),
        system_state={"mode": "normal"},
        device_state={"platform": "windows"},
        metadata={"source": "test"},
    )
