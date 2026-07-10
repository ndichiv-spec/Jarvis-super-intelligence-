from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest
from jarvis_communication.messages import BaseMessage, EventMessage, Pagination


def test_message_contracts_are_immutable_and_payload_is_frozen() -> None:
    message = EventMessage(
        message_name="event.snapshot",
        payload={"values": [1, 2, 3], "meta": {"k": "v"}},
    )

    assert message.payload["values"] == (1, 2, 3)

    with pytest.raises(TypeError):
        message.payload["meta"]["k"] = "updated"

    with pytest.raises(FrozenInstanceError):
        cast(Any, message).message_name = "event.changed"


def test_message_validation_raises_for_invalid_values() -> None:
    with pytest.raises(ValueError):
        BaseMessage(message_name="")

    with pytest.raises(ValueError):
        Pagination(page=0, page_size=10)

    with pytest.raises(ValueError):
        Pagination(page=1, page_size=0)
