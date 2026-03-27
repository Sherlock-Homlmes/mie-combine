# default
import asyncio
import traceback
from dataclasses import dataclass
from typing import Dict, List

import aiohttp

# library
import discord
from discord.ext import commands

# local
from core.env import env, is_dev_env
from models import connect_db

is_app_running = True


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fully_ready = asyncio.Event()
        self.module_count = 0

    async def wait_until_fully_ready(self):
        """Override wait_until_ready để thêm logic custom"""
        from bot.ai.guard_service import GuardViolationView
        from bot.confession import (
            ConfessionCreateButton,
            ConfessionEndButton,
            ConfessionPrivateReplyButton,
        )
        from bot.help import HelpView
        from bot.security.bad_words_check import (
            RemoveFalseBadWordButton,
            ReportFalseBadWordButton,
        )

        from .event_handlers import get_server_info

        # Connect DB
        if env.BOT_ONLY:
            await connect_db()
        await get_server_info()

        # Wait for bot ready
        await self.wait_until_ready()

        # Add persistent models
        for model in [
            ConfessionCreateButton,
            ConfessionEndButton,
            ConfessionPrivateReplyButton,
            RemoveFalseBadWordButton,
            ReportFalseBadWordButton,
            HelpView,
            GuardViolationView,
        ]:
            view = model(timeout=None)
            self.add_view(view)

        self._fully_ready.set()
        print(f"{self.user} ready")

    async def on_ready(self):
        global is_app_running
        await self.wait_until_fully_ready()

        if is_dev_env and not env.BOT_ONLY:
            # Stop bot when reload
            while is_app_running:
                from core.conf.api.event_handler import running

                if running:
                    await asyncio.sleep(1)
                else:
                    await self.close()
                    is_app_running = False

    # auto sync command on ready
    async def setup_hook(self):
        print("Loading extensions...")
        from bot import (
            admin_commands,
            ai,
            confession,
            create_vc,
            help,
            money,
            voice_channel,
        )
        from bot.errands import color as errand_color
        from bot.errands import topic as errand_topic
        from bot.errands import welcome as errand_welcome
        from bot.guild_event import on_member_join as guild_event_member_join
        from bot.guild_event import on_member_leave as guild_event_member_leave
        from bot.guild_event import on_member_update as guild_event_member_update
        from bot.schedule import monthly_leaderboard as shedule_monthly_leaderboard
        from bot.schedule import scan_user_name as schedule_scan_user_name
        from bot.schedule import static_channels as schedule_static_channels
        from bot.security import bad_words_check as security_bad_words_check
        from bot.security import cam_check as security_cam_check
        from bot.security import introduce_form as security_introduce_form
        from bot.study_time import commands as study_time_commands
        from bot.study_time import statistic as study_time_statistic
        from bot.study_time import study_time_log as study_time_study_time_log

        for module in [
            ai,
            create_vc,
            help,
            admin_commands,
            confession,
            money,
            voice_channel,
            #
            errand_color,
            errand_topic,
            errand_welcome,
            #
            guild_event_member_join,
            guild_event_member_leave,
            guild_event_member_update,
            #
            schedule_scan_user_name,
            shedule_monthly_leaderboard,
            schedule_static_channels,
            #
            security_bad_words_check,
            security_cam_check,
            security_introduce_form,
            #
            study_time_study_time_log,
            study_time_statistic,
            study_time_commands,
        ]:
            await module.setup(self)

        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_error(self, event, *args, **kwargs):
        error_details = str(traceback.format_exc())
        embed = {
            "embeds": [
                {
                    "title": "⚠️EVENT ERROR",
                    "description": error_details,
                    "color": 16711680,
                    "fields": [
                        {"name": "📝 Event", "value": event, "inline": False},
                    ],
                    "footer": {"text": "Error Handler"},
                }
            ]
        }
        await self.send_oops(embed)

    async def send_oops(self, content):
        if is_dev_env:
            return

        try:
            async with aiohttp.ClientSession() as session:
                if isinstance(content, dict):
                    await session.post(env.OOPS_WEBHOOK_URL, json=content)
                else:
                    await session.post(env.OOPS_WEBHOOK_URL, json={"content": content})
        except Exception as e:
            print(f"Can not send webhook: {e}")


@dataclass
class ServerRoleIds:
    admin: int = None
    feature_bot: int = None

    positive_student: int = None

    iron: int = None
    bronze: int = None
    silver: int = None
    gold: int = None
    diamond: int = None
    master: int = None
    challenger: int = None


@dataclass
class ServerRoles:
    every_one_role: discord.Role = None

    positive_student: discord.Role = None

    iron: discord.Role = None
    bronze: discord.Role = None
    silver: discord.Role = None
    gold: discord.Role = None
    diamond: discord.Role = None
    master: discord.Role = None
    challenger: discord.Role = None


@dataclass
class ServerChannels:
    leaderboard: discord.TextChannel = None
    general_chat: discord.TextChannel = None
    ai_logs: discord.TextChannel = None


# TODO: change to cluster role_id, role, channel, channel_id
@dataclass
class ServerInfo:
    # guild
    guild: discord.Guild = None
    # role_id
    role_ids = ServerRoleIds()
    # role
    roles = ServerRoles()
    every_one_role: discord.Role = None
    # channel
    channels = ServerChannels()
    # confession
    confession_dropdown_id: int = None
    confession_channel: discord.TextChannel = None
    manage_confession_channel: discord.TextChannel = None
    confession_count: int = None
    # schedule
    cap3_channel: discord.TextChannel = None
    thpt_channel: discord.TextChannel = None
    total_mem_channel: discord.TextChannel = None
    online_mem_channel: discord.TextChannel = None
    study_count_channel: discord.TextChannel = None
    # security
    bad_word_log_channel: discord.TextChannel = None
    false_bad_word_report_channel: discord.TextChannel = None
    admin_false_bad_word_log_channel: discord.TextChannel = None
    # create voice channel
    channel_cre: Dict = None
    # errands
    color_roles: List[int] = None
    game_roles: Dict = None
    welcome_channel: discord.TextChannel = None
    game_center_interaction_id: int = None


# START
guild_id = 880360143768924210
prefix = "dump,"
bot = Bot(command_prefix=prefix, intents=discord.Intents.all())
server_info = ServerInfo()


@bot.before_invoke
async def wait_before_command(_interaction):
    await bot._fully_ready.wait()


@bot.tree.error
async def on_command_error(interaction, error):
    try:
        await interaction.response.send_message(
            "Bot lỗi rồi. Bạn liên hệ <@890244740174467082> để được trợ giúp nhé!",
            ephemeral=True,
        )
    except Exception:
        await interaction.followup.send(
            "Bot lỗi rồi. Bạn liên hệ <@890244740174467082> để được trợ giúp nhé!",
            ephemeral=True,
        )

    error_details = str(traceback.format_exc())
    embed = {
        "embeds": [
            {
                "title": "⚠COMMAND ERROR",
                "description": error_details,
                "color": 16711680,
                "fields": [
                    {
                        "name": "📝 Command",
                        "value": f"/{interaction.command.qualified_name}",
                        "inline": False,
                    },
                    {
                        "name": "👤 User",
                        "value": interaction.user.mention
                        + f" (`{interaction.user.id}`)",
                        "inline": True,
                    },
                    {
                        "name": "🏠 Guild",
                        "value": interaction.guild.name + f" (`{interaction.guild.id}`)"
                        if interaction.guild
                        else "DM",
                        "inline": True,
                    },
                    {
                        "name": "📍 Channel",
                        "value": "DM"
                        if isinstance(interaction.channel, discord.DMChannel)
                        else interaction.channel.mention
                        + f" (`{interaction.channel.id}`)",
                        "inline": True,
                    },
                    {
                        "name": "🔗 Message Link",
                        "value": interaction.message.jump_url
                        if interaction.message
                        else "Not found",
                        "inline": False,
                    },
                ],
                "footer": {"text": "Error Handler"},
            }
        ]
    }
    await bot.send_oops(embed)
