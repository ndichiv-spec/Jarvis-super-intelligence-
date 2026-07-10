from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from jarvis_communication.context import ExecutionContext

MessageValue = Any


def _freeze_value(value: MessageValue) -> MessageValue:
    if isinstance(value, dict):
        frozen = {str(key): _freeze_value(item) for key, item in value.items()}
        return MappingProxyType(frozen)
    if isinstance(value, list | tuple | set | frozenset):
        return tuple(_freeze_value(item) for item in value)
    return value


def _freeze_mapping(values: Mapping[str, MessageValue]) -> Mapping[str, MessageValue]:
    return MappingProxyType({key: _freeze_value(value) for key, value in values.items()})


@dataclass(frozen=True, slots=True)
class Pagination:
    page: int
    page_size: int
    total_items: int | None = None

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if self.page_size < 1:
            raise ValueError("page_size must be >= 1")
        if self.total_items is not None and self.total_items < 0:
            raise ValueError("total_items must be >= 0")


@dataclass(frozen=True, slots=True)
class BaseMessage:
    message_name: str
    payload: Mapping[str, MessageValue] = field(default_factory=dict)
    context: ExecutionContext | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.message_name:
            raise ValueError("message_name must not be empty")
        object.__setattr__(self, "payload", _freeze_mapping(self.payload))
        object.__setattr__(self, "headers", MappingProxyType(dict(self.headers)))


@dataclass(frozen=True, slots=True)
class EventMessage(BaseMessage):
    topic: str | None = None


@dataclass(frozen=True, slots=True)
class CommandMessage[T](BaseMessage):
    expected_response: type[T] | None = None


@dataclass(frozen=True, slots=True)
class QueryMessage[T](BaseMessage):
    filters: Mapping[str, MessageValue] = field(default_factory=dict)
    pagination: Pagination | None = None
    expected_response: type[T] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "filters", _freeze_mapping(self.filters))


@dataclass(frozen=True, slots=True)
class NotificationMessage(BaseMessage):
    severity: str = "info"


@dataclass(frozen=True, slots=True)
class ErrorMessage(BaseMessage):
    code: str = "communication.error"
    detail: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.code:
            raise ValueError("code must not be empty")


@dataclass(frozen=True, slots=True)
class WarningMessage(BaseMessage):
    code: str = "communication.warning"
    detail: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.code:
            raise ValueError("code must not be empty")


@dataclass(frozen=True, slots=True)
class ResponseMessage[T]:
    request_message_id: str
    success: bool
    result: T | None = None
    errors: tuple[ErrorMessage, ...] = ()
    warnings: tuple[WarningMessage, ...] = ()
    metadata: Mapping[str, MessageValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_message_id:
            raise ValueError("request_message_id must not be empty")
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
