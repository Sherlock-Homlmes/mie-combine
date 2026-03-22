import discord

from models import AIMessageAuthor, ConversationHistory
from utils.time_modules import Now

LIMIT_NORMAL = 50
LIMIT_BOOSTER = 75
LIMIT_TESTER = 75
LIMIT_AD = 200


def get_limit(member: discord.Member) -> int:
    member_roles = str(member.roles)
    if "AD Carry" in member_roles:
        return LIMIT_AD
    if "Tester" in member_roles:
        return LIMIT_TESTER
    if "Server Booster" in member_roles:
        return LIMIT_BOOSTER
    return LIMIT_NORMAL


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
