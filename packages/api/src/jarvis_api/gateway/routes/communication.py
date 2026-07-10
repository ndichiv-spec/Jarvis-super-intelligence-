from __future__ import annotations

from fastapi import APIRouter, HTTPException

from jarvis_communication.engine import CommunicationEngine

router = APIRouter(prefix="/communication", tags=["communication"])

_engine: CommunicationEngine | None = None


def _get_engine() -> CommunicationEngine:
    global _engine
    if _engine is None:
        _engine = CommunicationEngine()
    return _engine


def _ok(data: object) -> dict:
    return {"ok": True, "data": data, "error": None, "metadata": {}}


def _error(status: int, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail=message)


@router.get("/conversations")
async def list_conversations(user_id: str | None = None):
    engine = _get_engine()
    if user_id:
        convs = await engine.conversations.list_by_participant(user_id)
    else:
        convs = list(engine.conversations._conversations.values())
    return _ok([{
        "conversation_id": c.conversation_id,
        "title": c.title,
        "participants": list(c.participants),
        "message_count": c.message_count,
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
        "is_archived": c.is_archived,
    } for c in convs])


@router.get("/messages")
async def list_messages(
    conversation_id: str | None = None,
    sender: str | None = None,
    receiver: str | None = None,
    limit: int = 50,
):
    engine = _get_engine()
    if conversation_id:
        msgs = await engine.messaging.list_by_conversation(conversation_id, limit=limit)
    elif sender:
        msgs = await engine.messaging.list_by_sender(sender, limit=limit)
    elif receiver:
        msgs = await engine.messaging.list_by_receiver(receiver, limit=limit)
    else:
        msgs = list(engine.messaging._messages.values())[:limit]
    return _ok([{
        "message_id": m.message_id,
        "sender": m.sender,
        "receiver": m.receiver,
        "channel": m.channel.value,
        "conversation_id": m.conversation_id,
        "message_type": m.message_type.value,
        "priority": m.priority.value,
        "body": m.body,
        "subject": m.subject,
        "timestamp": m.timestamp.isoformat(),
        "delivery_status": m.delivery_status.value,
        "read_status": m.read_status.value,
    } for m in msgs])


@router.post("/messages")
async def send_message(
    sender: str,
    receiver: str,
    body: str,
    conversation_id: str | None = None,
    subject: str | None = None,
    channel: str = "internal",
):
    engine = _get_engine()
    from jarvis_communication.models import ChannelType, CommunicationMessage, MessageType, Priority
    msg = CommunicationMessage(
        sender=sender,
        receiver=receiver,
        channel=ChannelType(channel),
        conversation_id=conversation_id,
        message_type=MessageType.TEXT,
        priority=Priority.NORMAL,
        body=body,
        subject=subject,
    )
    sent = await engine.send_message(msg)
    return _ok({
        "message_id": sent.message_id,
        "sender": sent.sender,
        "receiver": sent.receiver,
        "timestamp": sent.timestamp.isoformat(),
        "delivery_status": sent.delivery_status.value,
    })


@router.post("/email")
async def send_email(
    to_addresses: list[str],
    subject: str,
    body_text: str,
    sender: str = "system@jarvis.local",
    body_html: str | None = None,
):
    engine = _get_engine()
    from jarvis_communication.email import EmailMessage
    email = EmailMessage(
        to_addresses=tuple(to_addresses),
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        sender=sender,
    )
    sent = await engine.email.send(email)
    return _ok({
        "email_id": sent.email_id,
        "to": list(sent.to_addresses),
        "subject": sent.subject,
        "status": sent.status,
    })


@router.post("/notify")
async def send_notification(
    title: str,
    body: str,
    target_user: str | None = None,
    level: str = "info",
):
    engine = _get_engine()
    from jarvis_communication.models import Notification, NotificationLevel
    notification = Notification(
        title=title,
        body=body,
        level=NotificationLevel(level),
        source="api",
        target_user=target_user,
    )
    result = await engine.send_notification(notification)
    return _ok({
        "notification_id": result.notification_id,
        "title": result.title,
        "level": result.level.value,
        "timestamp": result.timestamp.isoformat(),
    })


@router.get("/notifications")
async def list_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
):
    engine = _get_engine()
    notifications = await engine.notifications.list_by_user(
        user_id, limit=limit, unread_only=unread_only,
    )
    return _ok([{
        "notification_id": n.notification_id,
        "title": n.title,
        "body": n.body,
        "level": n.level.value,
        "source": n.source,
        "read": n.read,
        "timestamp": n.timestamp.isoformat(),
    } for n in notifications])


@router.get("/presence")
async def list_presence():
    engine = _get_engine()
    all_presence = await engine.presence.list_all()
    return _ok([{
        "user_id": p.user_id,
        "status": p.status.value,
        "current_activity": p.current_activity,
        "last_seen": p.last_seen.isoformat() if p.last_seen else None,
        "connected_clients": p.connected_clients,
    } for p in all_presence])


@router.get("/metrics")
async def get_metrics():
    engine = _get_engine()
    summary = await engine.get_metrics_summary()
    return _ok(summary)


@router.get("/streams")
async def list_streams():
    engine = _get_engine()
    return _ok({
        "active_streams": engine.streaming.get_active_streams(),
        "count": engine.streaming.active_stream_count,
    })


@router.get("/unread/{user_id}")
async def get_unread_count(user_id: str):
    engine = _get_engine()
    msg_unread = await engine.messaging.count_unread(user_id)
    notif_unread = await engine.notifications.count_unread(user_id)
    return _ok({
        "messages": msg_unread,
        "notifications": notif_unread,
        "total": msg_unread + notif_unread,
    })


@router.post("/messages/{message_id}/read")
async def mark_message_read(message_id: str, user_id: str):
    engine = _get_engine()
    await engine.mark_read(message_id, user_id)
    return _ok({"status": "read"})


@router.post("/notifications/read-all")
async def mark_all_notifications_read(user_id: str):
    engine = _get_engine()
    count = await engine.notifications.mark_all_read(user_id)
    return _ok({"marked_read": count})
