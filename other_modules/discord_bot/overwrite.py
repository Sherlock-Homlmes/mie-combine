# default
from typing import Union

# lib
import discord

# local
from base import discord


class Overwrite(discord.PermissionOverwrite):
    async def create_confession(
        self,
        member: Union[discord.Member, discord.User],
        role: discord.Role,
        channel: Union[discord.VoiceChannel, discord.TextChannel],
    ):

        self.view_channel = False
        await channel.set_permissions(role, overwrite=self)
        self.view_channel = True
        await channel.set_permissions(member, overwrite=self)
