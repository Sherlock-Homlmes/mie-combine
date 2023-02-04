# default
from dataclasses import dataclass
import asyncio

# library
import discord
import beanie
from discord.ext import commands

# local
from models import *
from database.mongodb_async import client

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
    full_cam_category: discord.CategoryChannel = None
    cam_stream_category: discord.CategoryChannel = None


### START
guild_id = 880360143768924210
prefix = "dump,"
bot = Bot(command_prefix=prefix, intents=discord.Intents.all())
server_info = ServerInfo()


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


async def get_channel(guild: discord.Guild, channel_id: int):
    return await guild.fetch_channel(channel_id)


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
        "full_cam_category_id",
        "cam_stream_category_id",
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
        full_cam_category,
        cam_stream_category,
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
    server_info.full_cam_category = full_cam_category
    server_info.cam_stream_category = cam_stream_category


from bot_features import *
