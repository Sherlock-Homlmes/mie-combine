from datetime import datetime
from app.models import ConversationHistory, MessageEntry
from app.config import settings


async def get_history(user_id: str, channel_id: str) -> ConversationHistory:
    conv = await ConversationHistory.find_one(
        ConversationHistory.user_id == user_id,
        ConversationHistory.channel_id == channel_id,
    )
    if not conv:
        conv = ConversationHistory(user_id=user_id, channel_id=channel_id)
        await conv.insert()
    return conv


async def add_message(
    user_id: str,
    channel_id: str,
    guild_id: str,
    role: str,
    content: str,
    attachments: list[str] = None,
) -> ConversationHistory:
    conv = await get_history(user_id, channel_id)

    entry = MessageEntry(
        role=role,
        content=content,
        attachments=attachments or [],
    )
    conv.messages.append(entry)

    # Keep only last N messages
    max_msgs = settings.max_history_messages
    if len(conv.messages) > max_msgs:
        conv.messages = conv.messages[-max_msgs:]

    conv.guild_id = guild_id
    conv.updated_at = datetime.utcnow()
    await conv.save()
    return conv


async def get_recent_messages(
    user_id: str, channel_id: str, limit: int = None
) -> list[dict]:
    conv = await get_history(user_id, channel_id)
    msgs = conv.messages
    if limit:
        msgs = msgs[-limit:]
    return [
        {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
        for m in msgs
    ]
