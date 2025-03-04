# lib
import discord
from beanie.odm.operators.update.general import Set

# local
from core.conf.bot.conf import bot
from core.models import Users


# TODO: refactor this. duplicate with on_member_join
@bot.listen()
async def on_member_update(_: discord.Member, member_after: discord.Member):
    if not member_after.avatar:
        avatar = member_after.default_avatar.url
    else:
        avatar = member_after.avatar.url
    await Users.find_one(Users.discord_id == str(member_after.id)).upsert(
        Set(
            {
                Users.name: member_after.name,
                Users.nick: member_after.nick,
                Users.is_bot: member_after.bot,
                Users.avatar: avatar,
                Users.joined_at: member_after.joined_at,
            }
        ),
        on_insert=Users(
            discord_id=str(member_after.id),
            name=member_after.name,
            nick=member_after.nick,
            avatar=avatar,
            is_bot=member_after.bot,
            created_at=member_after.created_at,
            joined_at=member_after.joined_at,
        ),
    )
