import discord

from models import AIMessageAuthor, ConversationHistory
from utils.time_modules import Now

LIMIT_NORMAL = 30
LIMIT_BOOSTER = 150


def get_limit(member: discord.Member) -> int:
    if member.id == 880359404036317215:
        return 3
    return LIMIT_BOOSTER if "Server Booster" in str(member.roles) else LIMIT_NORMAL


async def check_rate_limit(
    member: discord.Member,
) -> tuple[bool, int]:
    """
    Returns: (allowed, remaining)
    Count message USER send today in history.
    """
    today = Now().today
    limit = get_limit(member)
    result = await ConversationHistory.aggregate(
        [
            {"$match": {"user_discord_id": member.id, "updated_at": {"$gte": today}}},
            {"$unwind": "$messages"},
            {
                "$match": {
                    "messages.role": AIMessageAuthor.USER,
                    "messages.created_at": {"$gte": today},
                }
            },
            {"$count": "total"},
        ]
    ).to_list()

    count = result[0]["total"] if result else 0

    return count <= limit, max(0, limit - count)
