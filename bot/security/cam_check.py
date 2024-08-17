# REFACTOR: better code
# default
import asyncio
from dataclasses import dataclass
from typing import List

# lib
import discord

# local
from core.conf.bot.conf import bot, server_info


@dataclass
class CheckCamEmbedMessage:
    # value input
    member: discord.Member = None
    check_types: List = None

    # value after create
    title: str = None
    description: str = None
    coulour: discord.Colour = None

    embed: discord.Embed = None
    message: discord.Message = None

    async def send(self):
        self.update_embed()
        try:
            self.message = await self.member.send(content=self.member.mention, embed=self.embed)
        except Exception as e:
            print("Cam check Error:", e)

    async def update(self):
        self.update_embed()
        try:
            await self.message.edit(embed=self.embed)
        except Exception as e:
            print("Cam check Error:", e)

    def update_embed(self):
        self.embed = discord.Embed(
            title=f"**{self.title}**",
            description=f"{self.member.name}, {self.description}",
            colour=self.coulour,
        )
        if self.member.avatar:
            pfp = self.member.avatar
        else:
            pfp = self.member.default_avatar.url
        self.embed.set_thumbnail(url=pfp)
        self.embed.set_footer(text="""BetterMe-Better everyday""")

    def warn(self):
        self.title = "Nhắc nhở"
        self.coulour = discord.Colour.orange()
        room_type = "/".join(self.check_types)
        self.description = f"bạn đang ở trong phòng FULL CAM. Hãy bật {room_type}, nếu không bạn sẽ bị kick sau 1 phút"

    def punish(self):
        self.title = "Nhắc nhở"
        self.coulour = discord.Colour.red()
        room_type = "/".join(self.check_types)
        self.description = f"bạn đã bị kick ra khỏi phòng vì không bật {room_type}"

    def thanks_for_accept(self):
        self.title = "Cảm ơn"
        self.coulour = discord.Colour.green()
        room_type = "/".join(self.check_types)
        self.description = f"cảm ơn bạn đã bật {room_type}"

    def thanks_for_leave(self):
        self.title = "Cảm ơn"
        self.description = "cảm ơn bạn đã rời phòng"
        self.coulour = discord.Colour.green()


check_cam_member_ids = []


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    global check_cam_member_ids

    full_cam_channels = server_info.full_cam_channels
    cam_stream_channels = server_info.cam_stream_channels
    sleep_time = [30, 50]
    check_channels = None

    if member_after.channel in full_cam_channels and member.id not in check_cam_member_ids:
        check_channels = full_cam_channels
        check_types = ["cam"]
    elif member_after.channel in cam_stream_channels and member.id not in check_cam_member_ids:
        check_channels = cam_stream_channels
        check_types = ["cam", "stream"]

    if check_channels:
        check_cam_member_ids.append(member.id)
        await asyncio.sleep(sleep_time[0])
        # remind
        if member.voice is not None:
            check_type_map = {
                "cam": member.voice.self_video,
                "stream": member.voice.self_stream,
            }
            if (
                not any(check_type_map[check_type] for check_type in check_types)
                and member.voice.channel in check_channels
            ):
                embed = CheckCamEmbedMessage(member=member, check_types=check_types)
                embed.warn()
                await embed.send()

                # kick
                await asyncio.sleep(sleep_time[1])
                if member.voice is not None:
                    if (
                        not any(check_type_map[check_type] for check_type in check_types)
                        and member.voice.channel in check_channels
                    ):
                        await member.move_to(None)
                        embed.punish()
                    else:
                        embed.thanks_for_accept()
                else:
                    embed.thanks_for_leave()

                await embed.update()
        check_cam_member_ids.remove(member.id)
