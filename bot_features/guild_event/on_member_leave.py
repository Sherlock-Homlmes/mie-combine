# lib
import discord
from beanie.odm.operators.update.general import Set

# local
from base import bot
from models import Users
from feature_func.time_modules import vn_now


@bot.listen()
async def on_member_remove(member: discord.Member):
    if not member.avatar:
        avatar = member.default_avatar.url
    else:
        avatar = member.avatar.url
    await Users.find_one(Users.discord_id == str(member.id)).upsert(
        Set(
            {
                Users.name: member.name,
                Users.avatar: avatar,
                Users.is_in_server: False,
                Users.leaved_at: vn_now(),
            }
        ),
        on_insert=Users(
            discord_id=str(member.id),
            name=member.name,
            avatar=avatar,
            is_in_server=False,
            created_at=member.created_at,
            joined_at=member.joined_at,
        ),
    )
    print(f"{member} have leaved server")
