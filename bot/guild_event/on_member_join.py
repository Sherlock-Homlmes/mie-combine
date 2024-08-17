# lib
import discord
from beanie.odm.operators.update.general import Set

# local
from core.conf.bot.conf import bot
from core.models import Users


@bot.listen()
async def on_member_join(member: discord.Member):
    if not member.avatar:
        avatar = member.default_avatar.url
    else:
        avatar = member.avatar.url
    await Users.find_one(Users.discord_id == str(member.id)).upsert(
        Set(
            {
                Users.name: member.name,
                Users.avatar: avatar,
                Users.joined_at: member.joined_at,
            }
        ),
        on_insert=Users(
            discord_id=str(member.id),
            name=member.name,
            avatar=avatar,
            created_at=member.created_at,
            joined_at=member.joined_at,
        ),
    )
    print(f"{member} have joined server")
