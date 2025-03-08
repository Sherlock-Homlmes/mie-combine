# default
import asyncio

# lib
from discord.ext import tasks

from bot.confession import check_bad_words

# local
from core.conf.bot.conf import bot, guild_id


@tasks.loop(hours=24)
async def scan_user_name():
    guild = bot.get_guild(guild_id)
    warning_members = []
    for member in guild.members:
        if not check_bad_words(member.name or "") or not check_bad_words(member.nick or ""):
            warning_members.append(member)

    for member in warning_members:
        await member.send("Tên của bạn có từ cấm. Hãy sửa lại tên phù hợp với quy định của server")
        await asyncio.sleep(1)
