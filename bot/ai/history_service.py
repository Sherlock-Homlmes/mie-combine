from models import ConversationHistory, MessageEntry
from utils.time_modules import vn_now


async def get_history(
    user_discord_id: int, channel_id: int, guild_id: int
) -> ConversationHistory:
    conv = await ConversationHistory.find_one(
        ConversationHistory.user_discord_id == user_discord_id,
        ConversationHistory.channel_id == channel_id,
        ConversationHistory.guild_id == guild_id,
    )
    if not conv:
        conv = ConversationHistory(
            user_discord_id=user_discord_id, channel_id=channel_id, guild_id=guild_id
        )
        await conv.insert()
    return conv


async def add_message(
    user_discord_id: int,
    channel_id: int,
    guild_id: int | None,
    role: str,
    content: str,
    attachments: list[str] = None,
) -> ConversationHistory:
    conv = await get_history(user_discord_id, channel_id, guild_id)

    entry = MessageEntry(
        role=role,
        content=content,
        attachments=attachments or [],
    )
    conv.messages.append(entry)
    conv.updated_at = vn_now()
    await conv.save()
    return conv


async def get_recent_messages(
    user_discord_id: int, channel_id: int, guild_id: int, limit: int = None
) -> list[dict]:
    conv = await get_history(user_discord_id, channel_id, guild_id)
    msgs = conv.messages
    if limit:
        msgs = msgs[-limit:]
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]
