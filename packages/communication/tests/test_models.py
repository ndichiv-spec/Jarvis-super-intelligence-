from __future__ import annotations

from datetime import UTC, datetime

from jarvis_communication.models import (
    ChannelType,
    CommunicationMessage,
    DeliveryStatus,
    MessageType,
    Priority,
    ReadStatus,
)


def test_communication_message_defaults() -> None:
    msg = CommunicationMessage()
    assert msg.message_id is not None
    assert msg.channel == ChannelType.INTERNAL
    assert msg.message_type == MessageType.TEXT
    assert msg.priority == Priority.NORMAL
    assert msg.delivery_status == DeliveryStatus.PENDING
    assert msg.read_status == ReadStatus.UNREAD


def test_communication_message_custom_values() -> None:
    ts = datetime.now(UTC)
    msg = CommunicationMessage(
        sender="alice",
        receiver="bob",
        channel=ChannelType.EMAIL,
        conversation_id="conv-1",
        timestamp=ts,
        message_type=MessageType.NOTIFICATION,
        priority=Priority.HIGH,
        body="Hello!",
        subject="Greeting",
        delivery_status=DeliveryStatus.SENT,
        read_status=ReadStatus.READ,
    )
    assert msg.sender == "alice"
    assert msg.receiver == "bob"
    assert msg.channel == ChannelType.EMAIL
    assert msg.conversation_id == "conv-1"
    assert msg.timestamp == ts
    assert msg.message_type == MessageType.NOTIFICATION
    assert msg.priority == Priority.HIGH
    assert msg.body == "Hello!"
    assert msg.subject == "Greeting"
    assert msg.delivery_status == DeliveryStatus.SENT
    assert msg.read_status == ReadStatus.READ


def test_attachment_defaults() -> None:
    from jarvis_communication.models import Attachment
    att = Attachment()
    assert att.attachment_id is not None
    assert att.content_type == "application/octet-stream"
    assert att.size == 0


def test_conversation_defaults() -> None:
    from jarvis_communication.models import Conversation
    conv = Conversation()
    assert conv.conversation_id is not None
    assert conv.is_archived is False
    assert conv.message_count == 0


def test_notification_defaults() -> None:
    from jarvis_communication.models import Notification, NotificationLevel
    notif = Notification()
    assert notif.notification_id is not None
    assert notif.level == NotificationLevel.INFO
    assert notif.read is False


def test_channel_defaults() -> None:
    from jarvis_communication.models import Channel
    channel = Channel()
    assert channel.is_active is True
    assert channel.channel_type == ChannelType.INTERNAL


def test_presence_info_defaults() -> None:
    from jarvis_communication.models import PresenceInfo, PresenceStatus
    info = PresenceInfo()
    assert info.status == PresenceStatus.OFFLINE
    assert info.connected_clients == 0


def test_session_defaults() -> None:
    from jarvis_communication.models import Session, SessionStatus
    session = Session()
    assert session.status == SessionStatus.ACTIVE
    assert session.client_info == ""


def all_enums_are_unique():
    from jarvis_communication.models import ChannelType, MessageType, Priority, DeliveryStatus, ReadStatus, NotificationLevel, MeetingStatus, SessionStatus, PresenceStatus, SubscriptionType
    for enum_cls in [ChannelType, MessageType, Priority, DeliveryStatus, ReadStatus, NotificationLevel, MeetingStatus, SessionStatus, PresenceStatus, SubscriptionType]:
        values = [e.value for e in enum_cls]
        assert len(values) == len(set(values)), f"{enum_cls.__name__} has duplicate values"
