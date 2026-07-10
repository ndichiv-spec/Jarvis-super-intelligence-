from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from jarvis_ai.models import (
    Message,
    ProviderKind,
    ProviderMetadata,
    ProviderRequest,
    RouteSelection,
    RuntimeRequest,
)


def _freeze(value: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(value or {}))


class PromptAssemblyError(ValueError):
    pass


class PromptAssemblyEngine:
    def assemble(
        self,
        request: RuntimeRequest,
        route: RouteSelection,
        provider: ProviderMetadata,
    ) -> ProviderRequest:
        instructions = request.instructions.strip()
        user_input = request.user_input.strip()
        if not instructions:
            raise PromptAssemblyError("Runtime request instructions are required.")
        if not user_input:
            raise PromptAssemblyError("Runtime user input is required.")

        system_instruction = self._build_system_instruction(
            instructions,
            request.context,
            provider.kind,
        )
        structured_output_schema = self._structured_output_schema(request.metadata)
        messages = self._build_messages(request.history, user_input, provider.kind)
        metadata = {
            "capability": request.capability.value,
            "provider_kind": provider.kind.value,
            "provider_id": provider.provider_id,
            "routing_mode": route.routing_mode.value,
        }

        return ProviderRequest.create(
            model_id=route.model_id,
            system_instruction=system_instruction,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            structured_output_schema=structured_output_schema,
            metadata=metadata,
        )

    def _build_system_instruction(
        self,
        instructions: str,
        context: Mapping[str, object],
        provider_kind: ProviderKind,
    ) -> str:
        context_lines = [
            f"{key}: {value}"
            for key, value in sorted(context.items(), key=lambda pair: pair[0])
        ]
        payload = [instructions]
        if context_lines:
            payload.append("Context:")
            payload.extend(context_lines)
        payload.append(self._provider_suffix(provider_kind))
        return "\n".join(line for line in payload if line)

    def _structured_output_schema(self, metadata: Mapping[str, object]) -> Mapping[str, object]:
        schema = metadata.get("structured_output_schema")
        if schema is None:
            return MappingProxyType({})
        if not isinstance(schema, Mapping):
            raise PromptAssemblyError("structured_output_schema must be a mapping when provided.")
        return _freeze(schema)

    def _build_messages(
        self,
        history: tuple[Message, ...],
        user_input: str,
        provider_kind: ProviderKind,
    ) -> tuple[Message, ...]:
        normalized_history = tuple(
            self._normalize_message(message, provider_kind) for message in history
        )
        user_message = self._normalize_message(
            Message(role="user", content=user_input),
            provider_kind,
        )
        return (*normalized_history, user_message)

    def _normalize_message(self, message: Message, provider_kind: ProviderKind) -> Message:
        role = message.role.strip().lower()
        if provider_kind == ProviderKind.GOOGLE and role == "assistant":
            return Message(role="model", content=message.content)
        if provider_kind == ProviderKind.ANTHROPIC and role == "system":
            return Message(role="assistant", content=message.content)
        return Message(role=role, content=message.content)

    def _provider_suffix(self, provider_kind: ProviderKind) -> str:
        if provider_kind == ProviderKind.OPENAI:
            return "Respond using a concise, reliable format."
        if provider_kind == ProviderKind.ANTHROPIC:
            return "Favor transparent reasoning summaries and safety-aware language."
        if provider_kind == ProviderKind.GOOGLE:
            return "Optimize for grounded and structured multimodal-ready outputs."
        if provider_kind == ProviderKind.OLLAMA:
            return "Optimize output for local inference determinism."
        if provider_kind == ProviderKind.VLLM:
            return "Optimize throughput-friendly responses for server inference."
        if provider_kind == ProviderKind.LOCAL:
            return "Prefer compact local-friendly responses."
        return "Follow runtime instructions exactly."
