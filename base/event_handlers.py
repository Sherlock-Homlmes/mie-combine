# default
from typing import Union, List
import asyncio

# lib
import discord
import beanie
from bson.int64 import Int64

# local
from .settings import bot, guild_id, server_info
from models import *
from database.mongodb_async import client


@bot.listen()
async def on_ready():
    global server_info

    ### Connect to database
    await beanie.init_beanie(
        database=client.discord_betterme,
        document_models=[Users, BadUsers, Confessions, ErrandData, VoiceChannels],
    )
    await get_server_info()

    print("Bot ready")


async def get_channel(guild: discord.Guild, channel_ids: Union[int, Int64, List]):
    if type(channel_ids) in [int, Int64]:
        return await guild.fetch_channel(channel_ids)
    elif type(channel_ids) == list:
        return await asyncio.gather(
            *[get_channel(guild, channel_id) for channel_id in channel_ids]
        )


async def get_server_info():
    ### Get server info
    server_info_data = await ErrandData.find_one(ErrandData.name == "server_info")
    server_info_data = server_info_data.value

    # get guild
    guild = await bot.fetch_guild(guild_id)

    channels = [
        # get confession channels
        "confession_channel_id",
        "manage_confession_channel_id",
        # get schedule channels
        "cap3_channel_id",
        "thpt_channel_id",
        "total_mem_channel_id",
        "online_mem_channel_id",
        "study_count_channel_id",
        # get security channels
        "diary_channel_id",
        "full_cam_channel_ids",
        "cam_stream_channel_ids",
    ]
    (
        confession_channel,
        manage_confession_channel,
        cap3_channel,
        thpt_channel,
        total_mem_channel,
        online_mem_channel,
        study_count_channel,
        diary_channel,
        full_cam_channels,
        cam_stream_channels,
    ) = await asyncio.gather(
        *[get_channel(guild, server_info_data[channel]) for channel in channels]
    )
    # set value
    server_info.guild = guild
    server_info.confession_channel = confession_channel
    server_info.manage_confession_channel = manage_confession_channel
    server_info.confession_dropdown_id = server_info_data["confession_dropdown_id"]
    server_info.cap3_channel = cap3_channel
    server_info.thpt_channel = thpt_channel
    server_info.total_mem_channel = total_mem_channel
    server_info.online_mem_channel = online_mem_channel
    server_info.study_count_channel = study_count_channel
    server_info.diary_channel = diary_channel
    server_info.admin_role_id = server_info_data["admin_role_id"]
    server_info.full_cam_channels = full_cam_channels
    server_info.cam_stream_channels = cam_stream_channels
