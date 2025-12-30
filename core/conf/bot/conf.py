# default
import asyncio
from dataclasses import dataclass
from typing import Dict, List
import traceback

# library
import discord
from discord.ext import commands
import aiohttp

# local
from core.env import env, is_dev_env
from core.models import connect_db

is_app_running = True


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fully_ready = asyncio.Event()

    async def wait_until_fully_ready(self):
        """Override wait_until_ready để thêm logic custom"""
        from .event_handlers import get_server_info
        from bot.confession import (
            ConfessionCreateButton,
            ConfessionEndButton,
            ConfessionPrivateReplyButton,
        )
        from bot.security.bad_words_check import RemoveFalseBadWordButton

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
                from core.event_handler import running

                if running:
                    await asyncio.sleep(1)
                else:
                    await self.close()
                    is_app_running = False

    # auto sync command on ready
    async def setup_hook(self):
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
    diary_channel: discord.TextChannel = None
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
                        "value": interaction.channel.mention
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
