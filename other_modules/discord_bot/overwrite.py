# default
from typing import Union

# lib
import discord


async def create_confession(
    member: Union[discord.Member, discord.User],
    channel: Union[discord.VoiceChannel, discord.TextChannel],
):
    # Set permission for member to see channel
    member_overwrite = discord.PermissionOverwrite()
    member_overwrite.view_channel = True
    await channel.set_permissions(member, overwrite=member_overwrite)
