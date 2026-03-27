# default
import asyncio
import datetime
from math import trunc

import aiohttp

# lib
from discord.ext import commands, tasks

# local
from core.conf.bot.conf import guild_id, server_info
from utils.time_modules import Now


class StaticChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Schedule - Static channels module ready")
        self.static_channels.start()

    @tasks.loop(minutes=10)
    async def static_channels(self):
        try:
            now = Now().now
            cap3day = datetime.datetime(now.year, 6, 6)
            thptday = datetime.datetime(now.year, 6, 12)
            if (cap3day - now).days < 0:
                cap3day = datetime.datetime(now.year + 1, 6, 6)
            if (thptday - now).days < 0:
                thptday = datetime.datetime(now.year + 1, 6, 12)

            cap3_left = cap3day - now
            thpt_left = thptday - now

            thpt = f"THPT: {thpt_left.days} ngày {trunc(thpt_left.seconds / 3600)} giờ"
            cap3 = f"Cấp 3: {cap3_left.days} ngày {trunc(cap3_left.seconds / 3600)} giờ"

            await asyncio.gather(
                *[
                    server_info.cap3_channel.edit(name=cap3),
                    server_info.thpt_channel.edit(name=thpt),
                ]
            )

            # server stats
            async with aiohttp.ClientSession() as session:
                res = await session.get(
                    url="https://discord.com/api/guilds/880360143768924210/widget.json"
                )
                resp = await res.json()

            guild = self.bot.get_guild(guild_id)
            voice_channel_list = guild.voice_channels
            total_voice_member = sum(
                len(channel.members) for channel in voice_channel_list
            )

            total_member = guild.member_count
            online_member = resp["presence_count"]

            await asyncio.gather(
                *[
                    server_info.total_mem_channel.edit(
                        name=f"Thành viên: {total_member} người"
                    ),
                    server_info.online_mem_channel.edit(
                        name=f"Online: {online_member} người"
                    ),
                    server_info.study_count_channel.edit(
                        name=f"Đang học: {total_voice_member} người"
                    ),
                ]
            )
        except Exception as e:
            print("Static channel error: ", e)


# TODO
def good_luck():
    pass


async def setup(bot):
    await bot.add_cog(StaticChannelsCog(bot))
