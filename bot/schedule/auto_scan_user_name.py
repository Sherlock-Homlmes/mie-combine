# default
import asyncio

# lib
import discord
from discord.ext import tasks

from bot.confession import check_bad_words

# local
from core.conf.bot.conf import server_info


@tasks.loop(hours=24)
async def scan_user_name():
    warning_members = []
    for member in server_info.guild.members:
        if not check_bad_words(member.name or "") or not check_bad_words(member.nick or ""):
            warning_members.append(member)

    for member in warning_members:
        try:
            await member.send(
                "Tên của bạn có từ cấm. Hãy sửa lại tên phù hợp với quy định của server"
            )
        except discord.errors.Forbidden:
            pass
        await asyncio.sleep(1)
