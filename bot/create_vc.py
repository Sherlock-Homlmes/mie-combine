# REFACTOR
# default
import asyncio
import datetime
from typing import Union

# lib
import discord
from discord import Interaction, app_commands
from discord.ext import commands

# local
from core.conf.bot.conf import guild_id, server_info
from models import ErrandData, Users, VoiceChannels
from utils.discord_bot.channel_name import (
    check_avaiable_name,
)
from utils.time_modules import Now

# ========== SHARED STATE ==========
all_created_vc_id: list[int] = []
is_ready = False
guild: discord.Guild = None
vc_id_name_map: dict[int, int] = {}


# ========== HELPER FUNCTIONS ==========
def find_first_missing_number(lst):
    num_set = set(lst)
    i = 1
    while i in num_set:
        i += 1
    return i


# ========== ROOM CLASS ==========
class Room:
    def __init__(self):
        self.number: int | None = None

    def get_new_room_number(self):
        self.number = find_first_missing_number(vc_id_name_map.values())

    def get_room_number_from_room_name(self, room_name: str):
        try:
            self.number = int(room_name.replace("#room ", ""))
        except ValueError:
            self.number = None


# ========== FIX ROOM FUNCTION ==========
# TODO: fix room include remove additional_category_ids
async def fix_room():
    global vc_id_name_map, guild, all_created_vc_id

    all_vc = [x.vc_id for x in await VoiceChannels.find({}).to_list()]
    all_vc.extend(all_created_vc_id)
    all_vc = set(all_vc)

    for vc_id in all_vc:
        vc_channel = guild.get_channel(vc_id)

        if vc_channel:
            if vc_channel.members == []:
                await vc_channel.delete()
                vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
                await vc.delete()
            else:
                room = Room()
                room.get_room_number_from_room_name(vc_channel.name)
                if room.number is not None:
                    vc_id_name_map[vc_id] = room.number
        else:
            vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
            await vc.delete()


# ========== ROOM PERMISSION ==========
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
    def from_interaction(cls, interaction: Interaction, *args, **kwargs):
        return cls(
            channel=interaction.user.voice.channel if interaction.user.voice else None,
            user=interaction.user,
            send_func=kwargs.pop("send_func", interaction.response.send_message),
            *args,
            **kwargs,
        )

    @classmethod
    def from_message(cls, message: discord.Message, *args, **kwargs):
        return cls(
            channel=message.author.voice.channel if message.author.voice else None,
            user=message.author,
            send_func=None,
            *args,
            **kwargs,
        )

    async def _send(self, message: str):
        if self._use_return:
            return message
        await self._send_func(message)
        return None

    async def _guard(self) -> str | None:
        """Return error string if invalid, None if OK"""
        global all_created_vc_id
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


# ========== COMMANDS COG ==========
class CreateVCCommands(commands.Cog):
    """Cog for voice channel commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="public", description="Cho phép mọi người vào phòng")
    async def public(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("public")

    @app_commands.command(
        name="private", description="Không cho phép mọi người vào phòng"
    )
    async def private(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("private")

    @app_commands.command(name="show", description="Hiện phòng cho mọi người thấy")
    async def show(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("show")

    @app_commands.command(name="hide", description="Ẩn phòng không cho mọi người thấy")
    async def hide(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("hide")

    @app_commands.command(name="mute", description="Tắt mic phòng")
    async def mute(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("mute")

    @app_commands.command(name="unmute", description="Mở mic phòng")
    async def unmute(self, interaction: Interaction):
        await RoomPermission.from_interaction(interaction).set_status("unmute")

    @app_commands.command(name="rename", description="Đặt lại tên phòng")
    async def rename(self, interaction: Interaction, name: str):
        await RoomPermission.from_interaction(interaction).rename(name)

    @app_commands.command(name="limit", description="Đặt giới hạn phòng")
    async def limit(self, interaction: Interaction, limit: int):
        await RoomPermission.from_interaction(interaction).set_limit(limit)

    @app_commands.command(name="invite", description="Mời bạn vào phòng")
    async def invite(self, interaction: Interaction):
        user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

        async def user_select_callback(callback_interaction: Interaction):
            members = await asyncio.gather(
                *[
                    callback_interaction.guild.fetch_member(member_id)
                    for member_id in callback_interaction.data["values"]
                ]
            )

            await RoomPermission.from_interaction(
                interaction, send_func=callback_interaction.response.send_message
            ).invite(members)

        user_select.callback = user_select_callback
        view = discord.ui.View(timeout=180)
        view.add_item(user_select)

        await interaction.response.send_message(view=view, delete_after=180)

    @app_commands.command(name="allow", description="Cho phép bạn vào phòng")
    async def allow(self, interaction: Interaction):
        user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

        async def user_select_callback(callback_interaction: Interaction):
            members = await asyncio.gather(
                *[
                    callback_interaction.guild.fetch_member(member_id)
                    for member_id in callback_interaction.data["values"]
                ]
            )
            await RoomPermission.from_interaction(
                interaction, send_func=callback_interaction.response.send_message
            ).allow(members)

        user_select.callback = user_select_callback
        view = discord.ui.View(timeout=180)
        view.add_item(user_select)

        await interaction.response.send_message(view=view, delete_after=180)

    @app_commands.command(name="kick", description="Kick khỏi phòng")
    @app_commands.describe(member="Some one")
    async def kick(
        self, interaction: Interaction, member: Union[discord.User, discord.Member]
    ):
        await RoomPermission.from_interaction(interaction).kick([member])


# ========== LISTENER COG ==========
class CreateVCListener(commands.Cog):
    """Cog for voice channel event listeners."""

    command_mess = """
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/hide: ẩn phòng với mọi người

/show: hiện phòng với mọi người

/mute: tắt mic phòng

/unmute: bật mic phòng

/allow: cho phép người bạn muốn vào phòng

/invite: mời người vào phòng

/kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/limit + [số_người_giới_hạn]

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Phòng sẽ mất khi không còn ai trong phòng
-Bạn có thể gọi bot trong kênh này
||Chúc bạn học vui :3||
"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global guild, is_ready, all_created_vc_id
        await self.bot._fully_ready.wait()
        # get all created voice channel
        guild = self.bot.get_guild(guild_id)
        all_created_vc_id.clear()
        all_created_vc_id.extend(
            [vc.vc_id for vc in await VoiceChannels.find({}).to_list()]
        )

        # delete empty voice channel
        await fix_room()
        is_ready = True
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Create VC module ready")

    @staticmethod
    def get_additional_category_id_channel_cre_id(category_id: int):
        for channel_cre_id, channel_cre in server_info.channel_cre.items():
            if category_id in channel_cre["additional_category_ids"]:
                return channel_cre_id
        return None

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        member_before: discord.VoiceState,
        member_after: discord.VoiceState,
    ):
        global all_created_vc_id
        if not is_ready:
            return

        voice_channel_before = member_before.channel
        voice_channel_after = member_after.channel

        # thứ tự: mem out -> mem in -> cre
        if voice_channel_after != voice_channel_before:
            # member out
            if voice_channel_before is not None:
                if voice_channel_before.id in all_created_vc_id:
                    await asyncio.sleep(5)
                    vc = await VoiceChannels.find_one(
                        VoiceChannels.vc_id == voice_channel_before.id
                    )
                    if not vc:
                        return

                    # TODO: refactor
                    if not len(voice_channel_before.members):
                        category_before_id = voice_channel_before.category.id
                        additional_category_channel_cre_id = (
                            self.get_additional_category_id_channel_cre_id(
                                category_before_id
                            )
                        )
                        category_channel_del = (
                            voice_channel_before.category
                            if additional_category_channel_cre_id
                            and len(voice_channel_before.category.channels) <= 1
                            else None
                        )
                        vc_channel_del = guild.get_channel(vc.vc_id)
                        del_list = [vc_channel_del, vc]
                        if category_channel_del:
                            del_list.append(category_channel_del)
                        await asyncio.gather(*[x.delete() for x in del_list if x])
                        all_created_vc_id.remove(voice_channel_before.id)
                        if vc_id_name_map.get(voice_channel_before.id):
                            del vc_id_name_map[voice_channel_before.id]
                        if category_channel_del:
                            server_info_data = await ErrandData.find_one(
                                ErrandData.name == "server_info"
                            )
                            server_info.channel_cre[additional_category_channel_cre_id][
                                "additional_category_ids"
                            ].remove(category_before_id)
                            server_info_data.value["channel_cre"][
                                additional_category_channel_cre_id
                            ]["additional_category_ids"] = server_info.channel_cre[
                                additional_category_channel_cre_id
                            ]["additional_category_ids"]
                            await server_info_data.save()

            # member in
            if voice_channel_after is not None:
                # set member's permission to text channel
                # create channel + set role
                if (
                    not member.bot
                    and voice_channel_after.id not in all_created_vc_id
                    and str(voice_channel_after.id) in server_info.channel_cre.keys()
                ):
                    if check_avaiable_name(member.name) is False:
                        await member.move_to(None)
                        await member.send(
                            "**Bạn hãy kiểm tra và đảm bảo trong tên của bạn không có từ cấm, tục tĩu**"
                        )
                    else:
                        channel_info = server_info.channel_cre[
                            str(voice_channel_after.id)
                        ]
                        room = Room()
                        room.get_new_room_number()
                        # create
                        vc_name = f"#room {room.number}"
                        feature_bot_role = server_info.guild.get_role(
                            server_info.role_ids.feature_bot
                        )
                        vc_channel: discord.VoiceChannel
                        try:
                            vc_channel = await voice_channel_after.category.create_voice_channel(
                                name=vc_name,
                                overwrites={
                                    server_info.guild.default_role: discord.PermissionOverwrite(
                                        view_channel=True, connect=False
                                    ),
                                    member: discord.PermissionOverwrite(
                                        view_channel=True, connect=True
                                    ),
                                    feature_bot_role: discord.PermissionOverwrite(
                                        view_channel=True, connect=True
                                    ),
                                },
                                user_limit=channel_info["limit"][1],
                            )
                        except discord.errors.HTTPException as e:
                            if e.code != 50035:
                                return
                            should_create_new_category = True
                            for category_id in server_info.channel_cre[
                                str(voice_channel_after.id)
                            ]["additional_category_ids"]:
                                try:
                                    category = await server_info.guild.fetch_channel(
                                        category_id
                                    )
                                    vc_channel = await category.create_voice_channel(
                                        name=vc_name,
                                        overwrites={
                                            server_info.guild.default_role: discord.PermissionOverwrite(
                                                view_channel=True, connect=False
                                            ),
                                            member: discord.PermissionOverwrite(
                                                view_channel=True, connect=True
                                            ),
                                            feature_bot_role: discord.PermissionOverwrite(
                                                view_channel=True, connect=True
                                            ),
                                        },
                                        user_limit=channel_info["limit"][1],
                                    )
                                    should_create_new_category = False
                                except discord.errors.NotFound as e:
                                    pass
                                except discord.errors.HTTPException:
                                    pass
                            if should_create_new_category:
                                # TODO: refactor room create
                                # TODO: refactor errand data update
                                # TODO: update to f-string when update python version
                                new_room_category = (
                                    await server_info.guild.create_category(
                                        "———("
                                        + channel_info["locate"]
                                        + str(
                                            len(channel_info["additional_category_ids"])
                                            + 2
                                        )
                                        + ")———"
                                    )
                                )
                                await new_room_category.move(
                                    after=voice_channel_after.category
                                )
                                vc_channel = await new_room_category.create_voice_channel(
                                    name=vc_name,
                                    overwrites={
                                        server_info.guild.default_role: discord.PermissionOverwrite(
                                            view_channel=True, connect=False
                                        ),
                                        member: discord.PermissionOverwrite(
                                            view_channel=True, connect=True
                                        ),
                                        feature_bot_role: discord.PermissionOverwrite(
                                            view_channel=True, connect=True
                                        ),
                                    },
                                    user_limit=channel_info["limit"][1],
                                )
                                server_info.channel_cre[str(voice_channel_after.id)][
                                    "additional_category_ids"
                                ].append(new_room_category.id)
                                server_info_data = await ErrandData.find_one(
                                    ErrandData.name == "server_info"
                                )
                                server_info_data.value["channel_cre"][
                                    str(voice_channel_after.id)
                                ]["additional_category_ids"] = server_info.channel_cre[
                                    str(voice_channel_after.id)
                                ]["additional_category_ids"]
                                await server_info_data.save()
                        all_created_vc_id.append(vc_channel.id)
                        vc_id_name_map[vc_channel.id] = room.number

                        data_voice_channel = VoiceChannels(
                            owner=await Users.find_one(Users.discord_id == member.id),
                            vc_id=vc_channel.id,
                            created_at=Now().now,
                        )
                        await data_voice_channel.insert()

                        try:
                            await member.move_to(vc_channel)
                            await vc_channel.send(f"<@{member.id}>" + self.command_mess)

                        except discord.errors.HTTPException:
                            await asyncio.gather(
                                *[x.delete() for x in [vc_channel, data_voice_channel]]
                            )
                            all_created_vc_id.remove(vc_channel.id)
                            del vc_id_name_map[vc_channel.id]


async def setup(bot: commands.Bot):
    await bot.add_cog(CreateVCCommands(bot))
    await bot.add_cog(CreateVCListener(bot))
