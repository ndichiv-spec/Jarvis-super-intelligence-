from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

ContextData = Mapping[str, object]


def _freeze_mapping(value: Mapping[str, object] | None) -> ContextData:
    return MappingProxyType(dict(value or {}))


class AICapability(StrEnum):
    CONVERSATION = "conversation"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    SPEECH_RECOGNITION = "speech_recognition"
    SPEECH_SYNTHESIS = "speech_synthesis"
    IMAGE_UNDERSTANDING = "image_understanding"
    STRUCTURED_OUTPUT = "structured_output"
    TOOL_CALLING = "tool_calling"
    CODE_GENERATION = "code_generation"


class ProviderKind(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    VLLM = "vllm"
    LOCAL = "local"
    FUTURE = "future"


class RoutingMode(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    FALLBACK = "fallback"
    PRIORITY = "priority"
    CAPABILITY = "capability"
    POLICY = "policy"


class StreamEventType(StrEnum):
    TOKEN = "token"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class RuntimeErrorCode(StrEnum):
    VALIDATION = "validation"
    ROUTING = "routing"
    EXECUTION = "execution"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class RuntimeRequest:
    capability: AICapability
    instructions: str
    user_input: str
    history: tuple[Message, ...]
    context: ContextData
    metadata: ContextData
    manual_provider_id: str | None
    manual_model_id: str | None
    priority_provider_ids: tuple[str, ...]
    allowed_provider_ids: tuple[str, ...]
    blocked_provider_ids: tuple[str, ...]
    policy_tags: frozenset[str]
    stream: bool
    max_tokens: int | None
    temperature: float | None

    @classmethod
    def create(
        cls,
        capability: AICapability,
        instructions: str,
        user_input: str,
        *,
        history: tuple[Message, ...] = (),
        context: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
        manual_provider_id: str | None = None,
        manual_model_id: str | None = None,
        priority_provider_ids: tuple[str, ...] = (),
        allowed_provider_ids: tuple[str, ...] = (),
        blocked_provider_ids: tuple[str, ...] = (),
        policy_tags: frozenset[str] | None = None,
        stream: bool = False,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> RuntimeRequest:
        return cls(
            capability=capability,
            instructions=instructions,
            user_input=user_input,
            history=history,
            context=_freeze_mapping(context),
            metadata=_freeze_mapping(metadata),
            manual_provider_id=manual_provider_id,
            manual_model_id=manual_model_id,
            priority_provider_ids=priority_provider_ids,
            allowed_provider_ids=allowed_provider_ids,
            blocked_provider_ids=blocked_provider_ids,
            policy_tags=policy_tags or frozenset(),
            stream=stream,
            max_tokens=max_tokens,
            temperature=temperature,
        )


@dataclass(frozen=True, slots=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True, slots=True)
class CostMetadata:
    input_per_1k_tokens: float
    output_per_1k_tokens: float
    currency: str = "USD"


@dataclass(frozen=True, slots=True)
class PerformanceMetadata:
    quality_score: float
    speed_score: float
    reliability_score: float


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    identifier: str
    provider_id: str
    capabilities: tuple[AICapability, ...]
    context_window: int
    token_limit: int
    supports_streaming: bool
    multimodal: bool
    version: str
    available: bool
    cost: CostMetadata
    performance: PerformanceMetadata
    tags: frozenset[str]
    priority: int


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    provider_id: str
    display_name: str
    kind: ProviderKind
    capabilities: tuple[AICapability, ...]
    supported_models: tuple[str, ...]
    available: bool = True
    priority: int = 100
    policy_tags: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    model_id: str
    system_instruction: str
    messages: tuple[Message, ...]
    max_tokens: int | None
    temperature: float | None
    structured_output_schema: ContextData
    metadata: ContextData

    @classmethod
    def create(
        cls,
        model_id: str,
        system_instruction: str,
        messages: tuple[Message, ...],
        *,
        max_tokens: int | None,
        temperature: float | None,
        structured_output_schema: Mapping[str, object] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> ProviderRequest:
        return cls(
            model_id=model_id,
            system_instruction=system_instruction,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            structured_output_schema=_freeze_mapping(structured_output_schema),
            metadata=_freeze_mapping(metadata),
        )


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    text: str
    provider_id: str
    model_id: str
    finish_reason: str
    usage: TokenUsage | None
    metadata: ContextData

    @classmethod
    def create(
        cls,
        text: str,
        provider_id: str,
        model_id: str,
        *,
        finish_reason: str = "completed",
        usage: TokenUsage | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> ProviderResponse:
        return cls(
            text=text,
            provider_id=provider_id,
            model_id=model_id,
            finish_reason=finish_reason,
            usage=usage,
            metadata=_freeze_mapping(metadata),
        )


@dataclass(frozen=True, slots=True)
class UnifiedResponse:
    text: str
    capability: AICapability
    provider_id: str
    model_id: str
    finish_reason: str
    usage: TokenUsage
    latency_ms: float
    duration_ms: float
    estimated_cost: float
    metadata: ContextData


@dataclass(frozen=True, slots=True)
class StreamEvent:
    event_type: StreamEventType
    text: str
    provider_id: str
    model_id: str
    metadata: ContextData

    @classmethod
    def create(
        cls,
        event_type: StreamEventType,
        text: str,
        provider_id: str,
        model_id: str,
        *,
        metadata: Mapping[str, object] | None = None,
    ) -> StreamEvent:
        return cls(
            event_type=event_type,
            text=text,
            provider_id=provider_id,
            model_id=model_id,
            metadata=_freeze_mapping(metadata),
        )


@dataclass(frozen=True, slots=True)
class RoutingPolicy:
    prefer_low_cost: bool = False
    prefer_low_latency: bool = False
    minimum_quality: float | None = None
    required_tags: frozenset[str] = frozenset()
    disallowed_tags: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 2
    timeout_seconds: float = 30.0
    backoff_seconds: tuple[float, ...] = (0.0, 0.05, 0.2)
    fallback_provider_ids: tuple[str, ...] = ()
    circuit_breaker_failures: int = 3
    circuit_breaker_reset_seconds: float = 30.0


@dataclass(frozen=True, slots=True)
class RouteSelection:
    provider_id: str
    model_id: str
    routing_mode: RoutingMode
    fallback_provider_ids: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RuntimeErrorDetail:
    code: RuntimeErrorCode
    message: str
    retriable: bool
