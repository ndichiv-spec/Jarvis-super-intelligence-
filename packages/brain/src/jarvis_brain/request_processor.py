from __future__ import annotations

from types import MappingProxyType

from jarvis_core import DomainIdentifier, Timestamp

from jarvis_brain.models import BrainRequest, ExecutionContext, RawBrainRequest


class DefaultRequestProcessor:
    def process(self, raw_request: RawBrainRequest) -> BrainRequest:
        execution_id = DomainIdentifier.new()
        received_at = Timestamp.now()
        trace_id = f"brain-{execution_id.value.hex}"
        normalized_message = " ".join(raw_request.message.strip().split())

        merged_context = MappingProxyType(
            {
                "conversation": raw_request.conversation_context,
                "user": raw_request.user_context,
                "memory_references": raw_request.memory_references,
                "knowledge_references": raw_request.knowledge_references,
                "workspace": raw_request.workspace_context,
                "active_projects": raw_request.active_projects,
                "system": raw_request.system_state,
                "device": raw_request.device_state,
            }
        )

        context = ExecutionContext(
            conversation_context=raw_request.conversation_context,
            user_context=raw_request.user_context,
            memory_references=raw_request.memory_references,
            knowledge_references=raw_request.knowledge_references,
            workspace_context=raw_request.workspace_context,
            active_projects=raw_request.active_projects,
            system_state=raw_request.system_state,
            device_state=raw_request.device_state,
            merged_context=merged_context,
        )

        return BrainRequest(
            execution_id=execution_id,
            trace_id=trace_id,
            received_at=received_at,
            normalized_message=normalized_message,
            context=context,
            metadata=raw_request.metadata,
        )
