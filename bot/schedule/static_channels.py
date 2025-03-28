# default
import asyncio
import datetime
from math import trunc

import aiohttp

# lib
from discord.ext import tasks

# local
from core.conf.bot.conf import bot, guild_id, server_info
from utils.time_modules import Now

total_member = 10000
online_member = 1000
total_voice_member = 50


@tasks.loop(minutes=10)
async def static_channels():
    global online_member, total_member, total_voice_member
    # count down

    now = Now().now
    cap3day = datetime.datetime(now.year, 6, 6)
    thptday = datetime.datetime(now.year, 6, 26)
    if (cap3day - now).days < 0:
        cap3day = datetime.datetime(now.year + 1, 6, 6)
    if (thptday - now).days < 0:
        thptday = datetime.datetime(now.year + 1, 6, 26)

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
        res = await session.get(url="https://discord.com/api/guilds/880360143768924210/widget.json")
        resp = await res.json()

    guild = bot.get_guild(guild_id)
    voice_channel_list = guild.voice_channels
    total_voice_member = sum(len(channel.members) for channel in voice_channel_list)

    total_member = guild.member_count
    online_member = resp["presence_count"]

    await asyncio.gather(
        *[
            server_info.total_mem_channel.edit(name=f"Thành viên: {total_member} người"),
            server_info.online_mem_channel.edit(name=f"Online: {online_member} người"),
            server_info.study_count_channel.edit(name=f"Đang học: {total_voice_member} người"),
        ]
    )


# TODO
def good_luck():
    pass


def discord_server_info():
    global total_member, online_member
    return {
        "total_member": total_member,
        "online_member": online_member,
        "total_voice_member": total_voice_member,
        "study_hour": 5,
    }
