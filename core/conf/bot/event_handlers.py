# default
import asyncio

from core.models import ErrandData
from utils.discord_bot.get_object import get_channel

# lib
# local
from .conf import bot, guild_id, server_info  # noqa: F401


async def get_server_info():
    global server_info

    ### Get server info
    server_info_data = await ErrandData.find_one(ErrandData.name == "server_info")
    server_info_data = server_info_data.value

    # Test data

    # server_info_data["confession_dropdown_id"] = 1280893469782708286
    # server_info_data["confession_channel_id"] = 1280890216504234067
    # server_info_data["manage_confession_channel_id"] = 1280891220838846544
    # server_info_data["diary_channel_id"] = 1329116022057472021
    # server_info_data["admin_false_bad_word_log_channel_id"] = 1329116331496439911

    # get guild
    server_info.guild = bot.get_guild(guild_id)
    server_info.roles.every_one_role = server_info.guild.get_role(server_info.guild.id)

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
        "admin_false_bad_word_log_channel_id",
        # errands
        "welcome_channel_id",
        "leaderboard_channel_id",
        "general_chat_channel_id",
    ]
    (
        server_info.confession_channel,
        server_info.manage_confession_channel,
        server_info.cap3_channel,
        server_info.thpt_channel,
        server_info.total_mem_channel,
        server_info.online_mem_channel,
        server_info.study_count_channel,
        server_info.diary_channel,
        server_info.admin_false_bad_word_log_channel,
        server_info.welcome_channel,
        server_info.channels.leaderboard,
        server_info.channels.general_chat,
    ) = await asyncio.gather(
        *[get_channel(server_info.guild, server_info_data[channel]) for channel in channels]
    )
    # set value

    # role id
    server_info.role_ids.admin = server_info_data["admin_role_id"]
    server_info.role_ids.feature_bot = server_info_data["feature_bot_role_id"]

    # confession
    server_info.confession_dropdown_id = server_info_data["confession_dropdown_id"]
    # create voice channel
    server_info.channel_cre = server_info_data["channel_cre"]

    # errands
    server_info.color_roles = server_info_data["color_roles"]
    server_info.game_roles = server_info_data["game_roles"]
    server_info.game_center_interaction_id = server_info_data["game_center_interaction_id"]

    # monthly role

    # TODO: add this to errand data
    server_info.role_ids.iron = 1346834532606672948
    server_info.role_ids.bronze = 1346835956669349910
    server_info.role_ids.silver = 1346834833296457798
    server_info.role_ids.gold = 1346834974908612700
    server_info.role_ids.diamond = 1346835233257029755
    server_info.role_ids.master = 1346835472982478890
    server_info.role_ids.challenger = 1346835593040232592

    server_info.roles.iron = server_info.guild.get_role(server_info.role_ids.iron)
    server_info.roles.bronze = server_info.guild.get_role(server_info.role_ids.bronze)
    server_info.roles.silver = server_info.guild.get_role(server_info.role_ids.silver)
    server_info.roles.gold = server_info.guild.get_role(server_info.role_ids.gold)
    server_info.roles.diamond = server_info.guild.get_role(server_info.role_ids.diamond)
    server_info.roles.master = server_info.guild.get_role(server_info.role_ids.master)
    server_info.roles.challenger = server_info.guild.get_role(server_info.role_ids.challenger)

    server_info.role_ids.positive_student = server_info_data["positive_student_role_id"]
    server_info.roles.positive_student = server_info.guild.get_role(
        server_info.role_ids.positive_student
    )
