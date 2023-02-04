# default
import datetime
from dataclasses import dataclass

# library
import discord
import beanie
from beanie.odm.operators.update.general import Set

from discord import Interaction, app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, has_role, MissingPermissions, context
from discord.utils import get
from discord.ui import View, Select

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
    # confession
    confession_dropdown_id: int = None
    confession_channel: discord.TextChannel = None
    manage_confession_channel: discord.TextChannel = None
    confession_count: int = None


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
        document_models=[Confessions, Users, ErrandData],
    )
    await get_server_info()

    # messages = [message async for message in manage_confession_channel.history(limit=1)]
    # messages.reverse()
    # for message in messages:
    #     embed = message.embeds[0]
    #     print(embed.description)
    #     print(embed.fields[0].value.split("||<@")[1].split(">||")[0])

    # members = [
    #     member
    #     async for member in guild.fetch_members(limit=None)
    #     if member.bot == False
    # ]
    # member_list = []
    # for member in members:
    #     print(member)
    #     if not member.avatar:
    #         avatar = member.default_avatar.url
    #     else:
    #         avatar = member.avatar.url
    #     member_list.append(
    #         Users(
    #             discord_id=str(member.id),
    #             name=member.name,
    #             avatar=avatar,
    #             created_at=member.created_at,
    #             joined_at=member.joined_at,
    #         )
    #     )
    # await Users.insert_many(member_list)

    print("Bot ready")


async def get_server_info():
    ### Get server info
    server_info_data = await ErrandData.find_one(ErrandData.name == "server_info")
    server_info_data = server_info_data.value

    # get guild
    guild = await bot.fetch_guild(guild_id)
    # get confession_channel
    confession_channel = await guild.fetch_channel(
        server_info_data["confession_channel_id"]
    )
    manage_confession_channel = await guild.fetch_channel(
        server_info_data["manage_confession_channel_id"]
    )
    # set value
    server_info.guild = guild
    server_info.confession_channel = confession_channel
    server_info.manage_confession_channel = manage_confession_channel
    server_info.confession_dropdown_id = server_info_data["confession_dropdown_id"]


from bot_features import *
