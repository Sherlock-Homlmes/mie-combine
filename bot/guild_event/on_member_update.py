# lib
import discord
from beanie.odm.operators.update.general import Set

# local
from core.conf.bot.conf import bot, server_info
from core.models import Users
from bot.ai import model


# TODO: refactor this. duplicate with on_member_join
@bot.listen()
async def on_member_update(member_before: discord.Member, member_after: discord.Member):
    await bot._fully_ready.wait()

    if not member_after.avatar:
        avatar = member_after.default_avatar.url
    else:
        avatar = member_after.avatar.url
    await Users.find_one(Users.discord_id == member_after.id).upsert(
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
            discord_id=member_after.id,
            name=member_after.name,
            nick=member_after.nick,
            avatar=avatar,
            is_bot=member_after.bot,
            created_at=member_after.created_at,
            joined_at=member_after.joined_at,
        ),
    )

    if "Server Booster" in member_after.roles and "Server Booster" not in str(
        member_before.roles
    ):
        chat = model.start_chat()
        generative_thanks = await chat.send_message_async(
            f"Viết 1 đoạn văn ngắn cảm ơn bạn {member_after.name} đã boost cho server betterme"
        )
        await server_info.channels.general_chat.send(
            content=f"{generative_thanks}<@{member_after.id}>",
        )
