from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import (
    CommunicationMessage,
    DeliveryReceipt,
    DeliveryStatus,
)


class DeliveryService:
    def __init__(self) -> None:
        self._receipts: dict[str, DeliveryReceipt] = {}

    async def confirm_delivery(
        self,
        message_id: str,
        recipient: str,
        *,
        context: ExecutionContext | None = None,
    ) -> DeliveryReceipt:
        receipt = DeliveryReceipt(
            message_id=message_id,
            recipient=recipient,
            delivered_at=datetime.now(UTC),
            status=DeliveryStatus.DELIVERED,
        )
        self._receipts[f"{message_id}:{recipient}"] = receipt
        return receipt

    async def confirm_read(
        self,
        message_id: str,
        recipient: str,
        *,
        context: ExecutionContext | None = None,
    ) -> DeliveryReceipt:
        receipt = DeliveryReceipt(
            message_id=message_id,
            recipient=recipient,
            delivered_at=datetime.now(UTC),
            read_at=datetime.now(UTC),
            status=DeliveryStatus.READ,
        )
        self._receipts[f"{message_id}:{recipient}"] = receipt
        return receipt

    async def report_failure(
        self,
        message_id: str,
        recipient: str,
        error: str,
        *,
        context: ExecutionContext | None = None,
    ) -> DeliveryReceipt:
        receipt = DeliveryReceipt(
            message_id=message_id,
            recipient=recipient,
            status=DeliveryStatus.FAILED,
            error=error,
        )
        self._receipts[f"{message_id}:{recipient}"] = receipt
        return receipt

    async def get_receipt(
        self,
        message_id: str,
        recipient: str,
        *,
        context: ExecutionContext | None = None,
    ) -> DeliveryReceipt | None:
        return self._receipts.get(f"{message_id}:{recipient}")

    async def get_receipts_for_message(
        self,
        message_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[DeliveryReceipt]:
        return [
            receipt
            for key, receipt in self._receipts.items()
            if key.startswith(f"{message_id}:")
        ]

    async def get_delivery_status(
        self,
        message_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, DeliveryStatus]:
        statuses: dict[str, DeliveryStatus] = {}
        for key, receipt in self._receipts.items():
            msg_id, recipient = key.split(":", 1)
            if msg_id == message_id:
                statuses[recipient] = receipt.status
        return statuses
