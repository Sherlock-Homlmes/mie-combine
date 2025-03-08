# default
import asyncio
from dataclasses import dataclass
from typing import Dict, List

# library
import discord
from discord.ext import commands

# local
from core.env import env, is_dev_env
from core.models import connect_db

is_app_running = True


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        global is_app_running
        from .event_handlers import get_server_info
        from bot.confession import (
            ConfessionCreateButton,
            ConfessionEndButton,
            ConfessionPrivateReplyButton,
        )
        from bot.security.bad_words_check import RemoveFalseBadWordButton

        if env.BOT_ONLY:
            await connect_db()
        await get_server_info()

        # persistent models
        for model in [
            ConfessionCreateButton,
            ConfessionEndButton,
            ConfessionPrivateReplyButton,
            RemoveFalseBadWordButton,
        ]:
            view = model(timeout=None)
            self.add_view(view)

        print(f"{self.user} ready")

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

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)


@dataclass
class ServerRoleIds:
    admin: int = None
    feature_bot: int = None

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
    full_cam_channels: List[discord.VoiceChannel] = None
    cam_stream_channels: List[discord.VoiceChannel] = None
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
