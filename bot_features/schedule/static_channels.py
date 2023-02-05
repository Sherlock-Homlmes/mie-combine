# default
import aiohttp
import datetime
from datetime import timedelta
from math import trunc

# lib
from discord.ext import tasks

# local
from base import server_info
from other_modules.time_modules import vn_now

total_member = 10000
online_member = 1000


@tasks.loop(minutes=6)
async def static_channels():
    global online_member, total_member
    # count down

    now = vn_now()
    cap3day = datetime.datetime(now.year, 6, 6)
    thptday = datetime.datetime(now.year, 7, 7)
    if (cap3day - now).days < 0:
        cap3day.year += 1
        thptday.year += 1

    cap3_left = cap3day - now - timedelta(hours=1)
    thpt_left = thptday - now - timedelta(hours=1)

    thpt = (
        "THPT: "
        + str(thpt_left.days)
        + " ngày "
        + str(trunc(thpt_left.seconds / 3600))
        + " giờ "
    )
    cap3 = (
        "Cấp 3: "
        + str(cap3_left.days)
        + " ngày "
        + str(trunc(cap3_left.seconds / 3600))
        + " giờ "
    )

    await server_info.cap3_channel.edit(name=cap3)
    await server_info.thpt_channel.edit(name=thpt)

    # server stats
    async with aiohttp.ClientSession() as session:
        res = await session.get(
            url="https://discord.com/api/guilds/880360143768924210/widget.json"
        )
        resp = await res.json()

    total_member = server_info.guild.member_count
    online_member = resp["presence_count"]

    voice_channel_list = server_info.guild.voice_channels
    total_voice_member = sum([len(channel.members) for channel in voice_channel_list])

    await server_info.total_mem_channel.edit(name=f"Thành viên: {total_member} người")
    await server_info.online_mem_channel.edit(name=f"Online: {online_member} người")
    await server_info.study_count_channel.edit(
        name=f"Đang học: {total_voice_member} người"
    )


def member_info():
    global total_member, online_member
    return (total_member, online_member)
