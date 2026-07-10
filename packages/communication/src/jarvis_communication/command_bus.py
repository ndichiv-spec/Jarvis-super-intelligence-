from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messages import CommandMessage, ErrorMessage, WarningMessage
from jarvis_communication.pipeline import PipelineEngine

CommandHandler = Callable[[CommandMessage[Any], ExecutionContext], Awaitable[Any]]


class CommandExecutionContract(Protocol):
    async def before_dispatch(
        self,
        command: CommandMessage[Any],
        context: ExecutionContext,
    ) -> None: ...

    async def after_dispatch(
        self,
        command: CommandMessage[Any],
        context: ExecutionContext,
        result: CommandResult[Any],
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class CommandResult[T]:
    success: bool
    value: T | None = None
    errors: tuple[ErrorMessage, ...] = ()
    warnings: tuple[WarningMessage, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


class CommandBus:
    def __init__(
        self,
        *,
        pipeline: PipelineEngine[CommandMessage[Any], Any] | None = None,
        execution_contracts: tuple[CommandExecutionContract, ...] = (),
    ) -> None:
        self._handlers: dict[str, CommandHandler] = {}
        self._pipeline = pipeline or PipelineEngine()
        self._execution_contracts = execution_contracts

    def register_handler(self, command_name: str, handler: CommandHandler) -> None:
        self._handlers[command_name] = handler

    async def dispatch(
        self,
        command: CommandMessage[Any],
        *,
        context: ExecutionContext | None = None,
    ) -> CommandResult[Any]:
        execution_context = context or command.context or ExecutionContext.new(source="command-bus")
        handler = self._handlers.get(command.message_name)
        if handler is None:
            error = ErrorMessage(
                message_name="command.not_registered",
                payload={"command_name": command.message_name},
                code="command.handler.not_registered",
                detail=f"No handler registered for command '{command.message_name}'",
                context=execution_context,
            )
            return CommandResult(success=False, errors=(error,))

        for contract in self._execution_contracts:
            await contract.before_dispatch(command, execution_context)

        try:
            result = await self._pipeline.execute(
                command,
                execution_context,
                lambda current_command: handler(current_command, execution_context),
            )
            response = CommandResult(success=True, value=result)
        except Exception as error:
            failure = ErrorMessage(
                message_name="command.execution_failed",
                payload={"command_name": command.message_name},
                code="command.execution.failed",
                detail=str(error),
                context=execution_context,
            )
            response = CommandResult(success=False, errors=(failure,))

        for contract in self._execution_contracts:
            await contract.after_dispatch(command, execution_context, response)
        return response
