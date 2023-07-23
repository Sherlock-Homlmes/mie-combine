# default
from typing import Union
import asyncio

# lib
import discord

# local
from bot import server_info


class Overwrite(discord.PermissionOverwrite):
    async def create_confession(
        self,
        member: Union[discord.Member, discord.User],
        channel: Union[discord.VoiceChannel, discord.TextChannel],
    ):
        global every_one_role

        # Set permission for everyone not see channel
        self.view_channel = False
        await channel.set_permissions(
            server_info.every_one_role,
            overwrite=self)

        # Set permission for member to see channel
        self.view_channel = True
        await channel.set_permissions(member, overwrite=self)
