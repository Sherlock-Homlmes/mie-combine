# default
import asyncio

# lib

# local
from .settings import bot, guild_id, server_info
from models import ErrandData
from other_modules.discord_bot.get_object import get_channel


@bot.listen()
async def on_ready():
    await get_server_info()
    print("Bot ready")


async def get_server_info():
    global server_info

    ### Get server info
    server_info_data = await ErrandData.find_one(ErrandData.name == "server_info")
    server_info_data = server_info_data.value

    # get guild
    server_info.guild = await bot.fetch_guild(guild_id)

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
        # errands
        "welcome_channel_id",
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
        welcome_channel,
    ) = await asyncio.gather(
        *[
            get_channel(server_info.guild, server_info_data[channel])
            for channel in channels
        ]
    )
    # set value

    # role
    server_info.admin_role_id = server_info_data["admin_role_id"]
    server_info.feature_bot_role_id = server_info_data["feature_bot_role_id"]

    # confession
    server_info.confession_channel = confession_channel
    server_info.manage_confession_channel = manage_confession_channel
    server_info.confession_dropdown_id = server_info_data["confession_dropdown_id"]
    # schedule
    server_info.cap3_channel = cap3_channel
    server_info.thpt_channel = thpt_channel
    server_info.total_mem_channel = total_mem_channel
    server_info.online_mem_channel = online_mem_channel
    server_info.study_count_channel = study_count_channel
    # security
    server_info.diary_channel = diary_channel
    server_info.full_cam_channels = full_cam_channels
    server_info.cam_stream_channels = cam_stream_channels
    # create voice channel
    server_info.channel_cre = server_info_data["channel_cre"]

    # errands
    server_info.color_roles = server_info_data["color_roles"]
    server_info.game_roles = server_info_data["game_roles"]
    server_info.welcome_channel = welcome_channel
