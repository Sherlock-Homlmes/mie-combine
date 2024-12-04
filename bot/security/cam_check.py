# REFACTOR: better code
# default
import asyncio
from dataclasses import dataclass
from typing import List

# lib
import discord

# local
from core.conf.bot.conf import bot


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
sleep_time = [30, 50]
cam_channel_names = [
    "full cam",
]
cam_stream_channel_names = [
    "cam/stream",
]


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    _: discord.VoiceState,
    member_after: discord.VoiceState,
):
    global check_cam_member_ids

    current_channel = member_after.channel
    if current_channel is None:
        return

    def get_channel_check_types(current_channel: discord.VoiceChannel) -> List[str] | None:
        if current_channel is None or member.id in check_cam_member_ids:
            return None
        channel_name = current_channel.name.lower()
        check_types = None
        if any(x in channel_name for x in cam_channel_names):
            check_types = ["cam"]
        elif any(x in channel_name for x in cam_stream_channel_names):
            check_types = ["cam", "stream"]
        return check_types

    def pass_conditions(check_types: List[str]) -> bool:
        if member.voice is None or member.voice.channel.id != current_channel_id:
            return "LEAVE"
        check_type_map = {
            "cam": member.voice.self_video,
            "stream": member.voice.self_stream,
        }
        if any(check_type_map[check_type] for check_type in check_types):
            return "PASS"
        else:
            return "FAIL"

    current_channel_id = current_channel.id
    check_types = get_channel_check_types(current_channel)
    if check_types is None:
        return

    check_cam_member_ids.append(member.id)
    await asyncio.sleep(sleep_time[0])
    try:
        # warn
        if pass_conditions(check_types) in ["LEAVE", "PASS"]:
            return

        embed = CheckCamEmbedMessage(member=member, check_types=check_types)
        embed.warn()
        await embed.send()

        # kick
        await asyncio.sleep(sleep_time[1])
        condition = pass_conditions(check_types)
        if condition == "PASS":
            embed.thanks_for_accept()
        elif condition == "FAIL":
            await member.move_to(None)
            embed.punish()
        else:
            embed.thanks_for_leave()
        await embed.update()

    finally:
        check_cam_member_ids.remove(member.id)
