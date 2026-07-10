from __future__ import annotations

from types import MappingProxyType

from jarvis_brain.models import BrainRequest, ExecutionContext


class MergeContextEngine:
    def build_context(self, request: BrainRequest) -> ExecutionContext:
        merged_context: dict[str, object] = dict(request.context.merged_context)
        merged_context.update(
            {
                "active_project_count": len(request.context.active_projects),
                "has_memory_references": bool(request.context.memory_references),
                "has_knowledge_references": bool(request.context.knowledge_references),
                "system_keys": tuple(sorted(request.context.system_state.keys())),
                "device_keys": tuple(sorted(request.context.device_state.keys())),
            }
        )

        return ExecutionContext(
            conversation_context=request.context.conversation_context,
            user_context=request.context.user_context,
            memory_references=request.context.memory_references,
            knowledge_references=request.context.knowledge_references,
            workspace_context=request.context.workspace_context,
            active_projects=request.context.active_projects,
            system_state=request.context.system_state,
            device_state=request.context.device_state,
            merged_context=MappingProxyType(merged_context),
        )
