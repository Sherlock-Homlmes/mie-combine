# REFACTOR: better code
# default
import asyncio
from dataclasses import dataclass
from typing import List

# lib
import discord

# local
from bot import bot, server_info


@dataclass
class CheckCamEmbedMessage:
    # value input
    member: discord.Member = None
    check_type: List = None

    # value after create
    title: str = None
    description: str = None
    coulour: discord.Colour = None

    embed: discord.Embed = None
    message: discord.Message = None

    async def send(self):
        self.update_embed()
        try:
            self.message = await self.member.send(
                content=self.member.mention, embed=self.embed
            )
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
        if self.check_type == ["cam"]:
            self.description = "bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút"
        elif self.check_type == ["cam", "stream"]:
            self.description = "bạn đang ở trong phòng CAM/STREAM. Hãy bật camera/stream, nếu không bạn sẽ bị kick sau 1 phút"

    def punish(self):
        self.title = "Nhắc nhở"
        self.coulour = discord.Colour.red()
        if self.check_type == ["cam"]:
            self.description = "bạn đã bị kick ra khỏi phòng vì không bật cam"
        elif self.check_type == ["cam", "stream"]:
            self.description = "bạn đã bị kick ra khỏi phòng vì không bật cam/tream"

    def thanks_for_accept(self):
        self.title = "Cảm ơn"
        self.coulour = discord.Colour.green()
        if self.check_type == ["cam"]:
            self.description = "cảm ơn bạn đã bật cam"
        elif self.check_type == ["cam", "stream"]:
            self.description = "cảm ơn bạn đã bật cam/stream"

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

    ### only cam
    if (
        member_after.channel in full_cam_channels
        and member.id not in check_cam_member_ids
    ):
        check_cam_member_ids.append(member.id)
        await asyncio.sleep(sleep_time[0])
        # remind
        if member.voice is not None:
            if (
                member.voice.self_video is False
                and member.voice.channel in full_cam_channels
            ):
                embed = CheckCamEmbedMessage(member=member, check_type=["cam"])
                embed.warn()
                await embed.send()

                # kick
                await asyncio.sleep(sleep_time[1])
                if member.voice is not None:
                    if (
                        member.voice.self_video is False
                        and member.voice.channel in full_cam_channels
                    ):
                        await member.move_to(None)
                        embed.punish()
                    else:
                        embed.thanks_for_accept()
                else:
                    embed.thanks_for_leave()

                await embed.update()
        check_cam_member_ids.remove(member.id)

    ### cam | stream
    if (
        member_after.channel in cam_stream_channels
        and member.id not in check_cam_member_ids
    ):
        check_cam_member_ids.append(member.id)
        await asyncio.sleep(sleep_time[0])
        # remind
        if member.voice is not None:
            if (
                not any([member.voice.self_video, member.voice.self_stream])
                and member.voice.channel in cam_stream_channels
            ):
                embed = CheckCamEmbedMessage(
                    member=member, check_type=["cam", "stream"]
                )
                embed.warn()
                await embed.send()

                # kick
                await asyncio.sleep(sleep_time[1])
                if member.voice is not None:
                    if (
                        not any([member.voice.self_video, member.voice.self_stream])
                        and member.voice.channel in cam_stream_channels
                    ):
                        await member.move_to(None)
                        embed.punish()
                    else:
                        embed.thanks_for_accept()
                else:
                    embed.thanks_for_leave()

                await embed.update()
        check_cam_member_ids.remove(member.id)
