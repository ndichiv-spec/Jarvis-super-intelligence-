from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.delivery import DeliveryService
from jarvis_communication.models import DeliveryStatus


@pytest.fixture
def service() -> DeliveryService:
    return DeliveryService()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_confirm_delivery(service: DeliveryService, context: ExecutionContext) -> None:
    receipt = await service.confirm_delivery("msg-1", "user-1", context=context)
    assert receipt.status == DeliveryStatus.DELIVERED
    assert receipt.message_id == "msg-1"
    assert receipt.recipient == "user-1"


@pytest.mark.asyncio
async def test_confirm_read(service: DeliveryService, context: ExecutionContext) -> None:
    receipt = await service.confirm_read("msg-1", "user-1", context=context)
    assert receipt.status == DeliveryStatus.READ
    assert receipt.read_at is not None


@pytest.mark.asyncio
async def test_report_failure(service: DeliveryService, context: ExecutionContext) -> None:
    receipt = await service.report_failure("msg-1", "user-1", "Connection timeout", context=context)
    assert receipt.status == DeliveryStatus.FAILED
    assert receipt.error == "Connection timeout"


@pytest.mark.asyncio
async def test_get_receipt(service: DeliveryService, context: ExecutionContext) -> None:
    await service.confirm_delivery("msg-1", "user-1", context=context)
    receipt = await service.get_receipt("msg-1", "user-1", context=context)
    assert receipt is not None
    assert receipt.status == DeliveryStatus.DELIVERED


@pytest.mark.asyncio
async def test_get_receipts_for_message(service: DeliveryService, context: ExecutionContext) -> None:
    await service.confirm_delivery("msg-1", "user-1", context=context)
    await service.confirm_read("msg-1", "user-2", context=context)
    receipts = await service.get_receipts_for_message("msg-1", context=context)
    assert len(receipts) == 2


@pytest.mark.asyncio
async def test_get_delivery_status(service: DeliveryService, context: ExecutionContext) -> None:
    await service.confirm_delivery("msg-1", "alice", context=context)
    await service.confirm_read("msg-1", "bob", context=context)
    await service.report_failure("msg-1", "charlie", "Error", context=context)
    statuses = await service.get_delivery_status("msg-1", context=context)
    assert statuses["alice"] == DeliveryStatus.DELIVERED
    assert statuses["bob"] == DeliveryStatus.READ
    assert statuses["charlie"] == DeliveryStatus.FAILED
