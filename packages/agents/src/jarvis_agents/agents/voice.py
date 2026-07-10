from __future__ import annotations

from jarvis_agents.agents.base import BaseAgent
from jarvis_agents.models import (
    AgentCapability,
    AgentPermission,
    AgentPermissionResource,
    AgentTask,
    AgentTaskResult,
    PermissionAccess,
)


class VoiceAgent(BaseAgent):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            name="Voice",
            description="Processes voice and audio, handles speech interactions and audio processing",
            capabilities=(
                AgentCapability(name="voice", description="Process voice and audio"),
                AgentCapability(name="translation", description="Translate between languages"),
                AgentCapability(name="communication", description="Handle communications"),
            ),
            permissions=(
                AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.KNOWLEDGE, access=PermissionAccess.READ),
                AgentPermission(resource=AgentPermissionResource.COMMUNICATION, access=PermissionAccess.WRITE),
            ),
            **kwargs,
        )

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        desc = task.description.lower()
        if "transcribe" in desc or "speech" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Speech transcribed for: {task.description}",
                metadata={"duration_seconds": "45", "confidence": "0.96"},
            )
        if "translate" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Translation completed for: {task.description}",
                metadata={"source_lang": "en", "target_lang": "fr"},
            )
        if "audio" in desc:
            return AgentTaskResult(
                success=True,
                output=f"Audio processing completed: {task.description}",
                metadata={"audio_format": "wav", "duration": "30s"},
            )
        return AgentTaskResult(
            success=True,
            output=f"Voice processing complete: {task.description}",
            metadata={"processing_type": "voice", "confidence": "0.93"},
        )
