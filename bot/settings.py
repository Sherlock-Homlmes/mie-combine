# default
from dataclasses import dataclass
from typing import List, Dict

# library
import discord
from discord.ext import commands


####### BOT #######
class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"We have logged in as {self.user} combine bot")

    async def setup_hook(self):
        # auto sync command on ready
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)


@dataclass
class ServerInfo:
    # guild
    guild: discord.Guild = None
    # role
    admin_role_id: int = None
    feature_bot_role_id: int = None
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
    full_cam_channels: List[discord.VoiceChannel] = None
    cam_stream_channels: List[discord.VoiceChannel] = None
    # create voice channel
    channel_cre: Dict = None
    # errands
    color_roles: List[int] = None
    game_roles: Dict = None
    welcome_channel: discord.TextChannel = None
    game_center_interaction_id: int = None


### START
guild_id = 880360143768924210
prefix = "dump,"
bot = Bot(command_prefix=prefix, intents=discord.Intents.all())
server_info = ServerInfo()
