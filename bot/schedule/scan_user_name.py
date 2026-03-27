# default
import asyncio

# lib
import discord
from discord.ext import commands, tasks

from bot.security.bad_words_check import check_bad_words

# local
from core.conf.bot.conf import server_info


class AutoScanUserNameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Auto scan user name module ready")
        self.scan_user_name.start()

    @tasks.loop(hours=24)
    async def scan_user_name(self):
        warning_members = []
        for member in server_info.guild.members:
            if not check_bad_words(member.name or "") or not check_bad_words(
                member.nick or ""
            ):
                warning_members.append(member)

        for member in warning_members:
            try:
                await member.send(
                    "Tên của bạn có từ cấm. Hãy sửa lại tên phù hợp với quy định của server"
                )
            except discord.errors.Forbidden:
                pass
            await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(AutoScanUserNameCog(bot))
