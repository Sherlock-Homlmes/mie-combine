# REFACTOR
# default
import asyncio
import datetime
from typing import Union

# lib
import discord
from discord import Interaction, app_commands

# local
from core.conf.bot.conf import bot, server_info
from models import VoiceChannels
from utils.discord_bot.channel_name import (
    check_avaiable_name,
)
from utils.time_modules import Now

from .vars import all_created_vc_id

room_permission_effect = {
    "public": {
        "overwrite": "connect",
        "permission": True,
        "message": "Phòng đã được mở cho mọi người vào",
    },
    "private": {
        "overwrite": "connect",
        "permission": False,
        "message": "Phòng đã được đóng cho mọi người vào",
    },
    "show": {
        "overwrite": "view_channel",
        "permission": True,
        "message": "Phòng đã được hiện cho mọi người thấy",
    },
    "hide": {
        "overwrite": "view_channel",
        "permission": False,
        "message": "Phòng đã được ẩn không cho mọi người thấy",
    },
    "mute": {
        "overwrite": "speak",
        "permission": False,
        "message": "Đã tắt âm phòng",
    },
    "unmute": {
        "overwrite": "speak",
        "permission": True,
        "message": "Đã bỏ tắt âm phòng",
    },
}


class RoomPermission:
    def __init__(self, channel, user, send_func=None):
        self.channel = channel
        self.user = user
        self._send_func = send_func
        self._use_return = send_func is None

    @classmethod
    def from_interaction(cls, interaction: Interaction):
        return cls(
            channel=interaction.user.voice.channel if interaction.user.voice else None,
            user=interaction.user,
            send_func=interaction.response.send_message,
        )

    @classmethod
    def from_message(cls, message: discord.Message):
        return cls(
            channel=message.author.voice.channel if message.author.voice else None,
            user=message.author,
            send_func=None,  # return string instead
        )

    async def _send(self, message: str):
        if self._use_return:
            return message
        await self._send_func(message)
        return None

    async def _guard(self) -> str | None:
        """Return error string if invalid, None if OK"""
        if not self.channel or self.channel.id not in all_created_vc_id:
            return "Bạn không ở trong phòng được tạo bởi Mie"
        return None

    async def set_status(self, status: str) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)
        if status not in room_permission_effect:
            return await self._send("Trạng thái không hợp lệ")

        effect = room_permission_effect[status]
        overwrite = discord.PermissionOverwrite()
        setattr(overwrite, effect["overwrite"], effect["permission"])

        await self.channel.set_permissions(
            server_info.guild.default_role, overwrite=overwrite
        )
        return await self._send(effect["message"])

    async def rename(self, name: str) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)

        member_role_names = [role.name for role in self.user.roles]
        is_server_booster = "Server Booster" in member_role_names
        channel_data = await VoiceChannels.find_one(
            VoiceChannels.vc_id == self.channel.id
        )
        now = Now().now
        is_old_enough = (channel_data.created_at - datetime.timedelta(days=7)) < now

        if not is_server_booster and not is_old_enough:
            return await self._send(
                "Nâng cấp lên server booster hoặc giữ phòng trên 1 tuần để đổi tên nhé 😁"
            )
        if not check_avaiable_name(name):
            return await self._send(
                "**Không được đổi tên kênh có những từ cấm nha mầy, tau táng cho á**"
            )
        if len(name) > 50:
            return await self._send("Tên quá dài")

        await self.channel.edit(name=name)
        return await self._send("Tên kênh đã được đổi thành " + name)

    async def set_limit(self, limit: int) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)

        category_id = self.channel.category.id
        for _, value in server_info.channel_cre.items():
            if value["category_id"] != category_id:
                continue
            min_l, max_l = value["limit"]
            if min_l == max_l:
                return await self._send(
                    "Bạn không thể đặt limit cho phòng " + value["locate"]
                )
            if limit < min_l:
                return await self._send(
                    f"Bạn không thể đặt limit phòng {value['locate']} bé hơn {min_l}"
                )
            if limit > max_l:
                return await self._send(
                    f"Bạn không thể đặt limit phòng {value['locate']} lớn hơn {max_l}"
                )

            await self.channel.edit(user_limit=limit)
            return await self._send(f"**Đã đặt limit cho phòng:** {limit}")

    async def kick(self, members: list[discord.Member]) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)

        for member in members:
            is_owner = await VoiceChannels.find_one(
                VoiceChannels.owner.discord_id == member.id,
                VoiceChannels.vc_id == self.channel.id,
                fetch_links=True,
            )
            if is_owner:
                return await self._send("Bạn không thể kick chủ phòng")

            overwrite = discord.PermissionOverwrite(connect=False)
            await self.channel.set_permissions(member, overwrite=overwrite)
            if member in self.channel.members:
                await member.move_to(None)
        member_mentions = ", ".join([f"<@{member.id}>" for member in members])
        return await self._send(f"{member_mentions} đã mất quyền vào phòng")

    async def allow(self, members: list[discord.Member]) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)

        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        overwrite.connect = True
        await asyncio.gather(
            *[
                self.channel.set_permissions(member, overwrite=overwrite)
                for member in members
            ]
        )

        member_mentions = ", ".join([f"<@{member.id}>" for member in members])
        return await self._send(f"Đã cấp quyền cho {member_mentions} vào phòng")

    async def invite(self, members: list[discord.Member]) -> str | None:
        guard = await self._guard()
        if guard:
            return await self._send(guard)

        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        overwrite.connect = True
        await asyncio.gather(
            *[
                self.channel.set_permissions(member, overwrite=overwrite)
                for member in members
            ]
        )
        invite_link = await self.channel.create_invite(max_uses=1, unique=True)

        try:
            await asyncio.gather(
                *[
                    member.send(
                        f"**{self.user.name}** đã mời bạn vào học: {invite_link}"
                    )
                    for member in members
                ]
            )
        except discord.errors.HTTPException as e:
            print("Create vc invite Error: ", e)

        member_mentions = ", ".join([f"<@{member.id}>" for member in members])
        return await self._send(f"Đã mời {member_mentions} vào phòng")


async def get_list_members(member_ids: list[int | str]) -> list[discord.Member]:
    return await asyncio.gather(
        *[server_info.guild.fetch_member(int(member_id)) for member_id in member_ids]
    )


@bot.tree.command(name="public", description="Cho phép mọi người vào phòng")
async def public(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("public")


@bot.tree.command(name="private", description="Không cho phép mọi người vào phòng")
async def private(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("private")


@bot.tree.command(name="show", description="Hiện phòng cho mọi người thấy")
async def show(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("show")


@bot.tree.command(name="hide", description="Ẩn phòng không cho mọi người thấy")
async def hide(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("hide")


@bot.tree.command(name="mute", description="Tắt mic phòng")
async def mute(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("mute")


@bot.tree.command(name="unmute", description="Mở mic phòng")
async def unmute(interaction: Interaction):
    await RoomPermission.from_interaction(interaction).set_status("unmute")


@bot.tree.command(name="rename", description="Đặt lại tên phòng")
async def rename(interaction: Interaction, name: str):
    await RoomPermission.from_interaction(interaction).rename(name)


@bot.tree.command(name="limit", description="Đặt giới hạn phòng")
async def limit(interaction: Interaction, limit: int):
    await RoomPermission.from_interaction(interaction).set_limit(limit)


@bot.tree.command(name="invite", description="Mời bạn vào phòng")
async def invite(interaction: Interaction):
    user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

    async def user_select_callback(callback_interaction: Interaction):
        members = await asyncio.gather(
            *[
                callback_interaction.guild.fetch_member(member_id)
                for member_id in callback_interaction.data["values"]
            ]
        )

        room_perm = RoomPermission.from_interaction(interaction)
        result = await room_perm.invite(members)
        await callback_interaction.response.send_message(result)

    user_select.callback = user_select_callback
    view = discord.ui.View(timeout=180)
    view.add_item(user_select)

    await interaction.response.send_message(view=view, delete_after=180)


@bot.tree.command(name="allow", description="Cho phép bạn vào phòng")
async def allow(interaction: Interaction):
    user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

    async def user_select_callback(callback_interaction: Interaction):
        members = await asyncio.gather(
            *[
                callback_interaction.guild.fetch_member(member_id)
                for member_id in callback_interaction.data["values"]
            ]
        )

        room_perm = RoomPermission.from_interaction(interaction)
        result = await room_perm.allow(members)
        await callback_interaction.response.send_message(result)

    user_select.callback = user_select_callback
    view = discord.ui.View(timeout=180)
    view.add_item(user_select)

    await interaction.response.send_message(view=view, delete_after=180)


@bot.tree.command(name="kick", description="Kick khỏi phòng")
@app_commands.describe(member="Some one")
async def kick(interaction: Interaction, member: Union[discord.User, discord.Member]):
    await RoomPermission.from_interaction(interaction).kick([member])
