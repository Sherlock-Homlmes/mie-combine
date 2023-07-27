# default
from typing import Union
import asyncio

# lib
import discord


class Overwrite(discord.PermissionOverwrite):
    async def create_confession(
        self,
        member: Union[discord.Member, discord.User],
        channel: Union[discord.VoiceChannel, discord.TextChannel],
    ):
        # Set permission for member to see channel
        self.view_channel = True
        await channel.set_permissions(member, overwrite=self)
