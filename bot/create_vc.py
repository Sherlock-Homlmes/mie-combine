# REFACTOR
# default
import asyncio
from typing import Optional, Union

# lib
import discord
from discord import Interaction, PermissionOverwrite, app_commands
from discord.ext.commands import has_role
from discord.ui import View

# local
from core.conf.bot.conf import bot, guild_id, server_info
from core.models import ErrandData, Users, VoiceChannels
from utils.discord_bot.channel_name import (
    check_avaiable_name,
)
from utils.time_modules import Now

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


# ----------START-----------
all_created_vc_id = []
vc_id_name_map = {}
guild: discord.Guild = None
is_ready = False


class Room:
    def __init__(self):
        self.number = None

    def get_new_room_number(self):
        self.number = find_first_missing_number(vc_id_name_map.values())

    def get_room_number_from_room_name(self, room_name: str):
        try:
            self.number = int(room_name.replace("#room ", ""))
        except ValueError:
            self.number = None


def find_first_missing_number(lst):
    num_set = set(lst)
    i = 1
    while i in num_set:
        i += 1
    return i


@bot.listen()
async def on_ready():
    global all_created_vc_id, guild, is_ready

    print("6.Create voice channel ready")
    await asyncio.sleep(10)
    # get all created voice channel
    guild = bot.get_guild(guild_id)
    all_created_vc_id = [vc.vc_id for vc in await VoiceChannels.find({}).to_list()]

    # delete empty voice channel
    await fix_room()
    is_ready = True


# TODO: fix room include remove additional_category_ids
async def fix_room():
    global all_created_vc_id, guild

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
                if room.get_room_number_from_room_name(vc_channel.name) is not None:
                    vc_id_name_map[vc_id] = room.number

        else:
            vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
            await vc.delete()

    print("fix voice channel done")


def get_additional_category_id_channel_cre_id(category_id: int):
    for channel_cre_id, channel_cre in server_info.channel_cre.items():
        if category_id in channel_cre["additional_category_ids"]:
            return channel_cre_id
    return None


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    global all_created_vc_id, guild, is_ready

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
                vc = await VoiceChannels.find_one(VoiceChannels.vc_id == voice_channel_before.id)

                # TODO: refactor
                if not len(voice_channel_before.members):
                    category_before_id = voice_channel_before.category.id
                    additional_category_channel_cre_id = get_additional_category_id_channel_cre_id(
                        category_before_id
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
                        server_info_data.value["channel_cre"][additional_category_channel_cre_id][
                            "additional_category_ids"
                        ] = server_info.channel_cre[additional_category_channel_cre_id][
                            "additional_category_ids"
                        ]
                        await server_info_data.save()

        # member in
        if voice_channel_after is not None:
            # set member's permission to text channel
            # create channel + set role
            if (
                voice_channel_after.id not in all_created_vc_id
                and str(voice_channel_after.id) in server_info.channel_cre.keys()
            ):
                if check_avaiable_name(member.name) is False:
                    await member.move_to(None)
                    await member.send(
                        "**Bạn hãy kiểm tra và đảm bảo trong tên của bạn không có từ cấm, tục tĩu**"
                    )
                else:
                    channel_info = server_info.channel_cre[str(voice_channel_after.id)]
                    room = Room()
                    room.get_new_room_number()
                    # create
                    vc_name = f"#room {room.number}"
                    feature_bot_role = server_info.guild.get_role(server_info.role_ids.feature_bot)
                    vc_channel: discord.VoiceChannel
                    try:
                        vc_channel = await voice_channel_after.category.create_voice_channel(
                            name=vc_name,
                            overwrites={
                                server_info.guild.default_role: PermissionOverwrite(
                                    view_channel=True, connect=False
                                ),
                                member: PermissionOverwrite(view_channel=True, connect=True),
                                feature_bot_role: PermissionOverwrite(
                                    view_channel=True, connect=True
                                ),
                            },
                            user_limit=channel_info["limit"][1],
                        )
                    except discord.errors.HTTPException as e:
                        # TODO: remove this print
                        print("-------------", e.code, e.text)
                        if e.code != 50035:
                            return
                        should_create_new_category = True
                        for category_id in server_info.channel_cre[str(voice_channel_after.id)][
                            "additional_category_ids"
                        ]:
                            try:
                                category = await server_info.guild.fetch_channel(category_id)
                                vc_channel = await category.create_voice_channel(
                                    name=vc_name,
                                    overwrites={
                                        server_info.guild.default_role: PermissionOverwrite(
                                            view_channel=True, connect=False
                                        ),
                                        member: PermissionOverwrite(
                                            view_channel=True, connect=True
                                        ),
                                        feature_bot_role: PermissionOverwrite(
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
                            new_room_category = await server_info.guild.create_category(
                                "———("
                                + channel_info["locate"]
                                + str(len(channel_info["additional_category_ids"]) + 2)
                                + ")———"
                            )
                            await new_room_category.move(after=voice_channel_after.category)
                            vc_channel = await new_room_category.create_voice_channel(
                                name=vc_name,
                                overwrites={
                                    server_info.guild.default_role: PermissionOverwrite(
                                        view_channel=True, connect=False
                                    ),
                                    member: PermissionOverwrite(view_channel=True, connect=True),
                                    feature_bot_role: PermissionOverwrite(
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
                            server_info_data.value["channel_cre"][str(voice_channel_after.id)][
                                "additional_category_ids"
                            ] = server_info.channel_cre[str(voice_channel_after.id)][
                                "additional_category_ids"
                            ]
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
                        await vc_channel.send(f"<@{member.id}>" + command_mess)

                    except discord.errors.HTTPException:
                        await asyncio.gather(
                            *[x.delete() for x in [vc_channel, data_voice_channel]]
                        )
                        all_created_vc_id.remove(vc_channel.id)
                        del vc_id_name_map[vc_channel.id]


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


# slash command
async def room_permission(
    interaction: Interaction,
    status: Optional[str] = None,
    name: Optional[str] = None,
    limit: Optional[int] = None,
    member: Optional[Union[discord.User, discord.Member]] = None,
):
    global room_permission_effect
    current_channel = interaction.user.voice.channel
    send = interaction.response.send_message
    overwrite = discord.PermissionOverwrite()

    if current_channel:
        if current_channel.id in all_created_vc_id:
            if status in room_permission_effect.keys():
                setattr(
                    overwrite,
                    room_permission_effect[status]["overwrite"],
                    room_permission_effect[status]["permission"],
                )
                message = room_permission_effect[status]["message"]

                await current_channel.set_permissions(
                    server_info.guild.default_role, overwrite=overwrite
                )
                await send(message)

            if name:
                if check_avaiable_name(name):
                    new_name = name
                    if len(new_name) > 50:
                        await send("Tên quá dài")
                    else:
                        await current_channel.edit(name=new_name)
                        await send("Tên kênh đã được đổi thành " + new_name)
                else:
                    await send(
                        "**Không được đổi tên kênh có những từ cấm nha mầy, tau táng cho á**"
                    )

            if limit:
                category_id = current_channel.category.id
                for _, value in server_info.channel_cre.items():
                    if value["category_id"] == category_id:
                        if value["limit"][0] == value["limit"][1]:
                            await send("Bạn không thể đặt limit cho phòng " + value["locate"])
                        elif limit >= value["limit"][0] and limit <= value["limit"][1]:
                            await current_channel.edit(user_limit=limit)
                            await send(f"**Đã đặt limit cho phòng:** {limit}")
                        elif limit < value["limit"][0]:
                            await send(
                                f'Bạn không thể đặt limit phòng {value["locate"]} bé hơn {value["limit"][0]}'
                            )
                        elif limit > value["limit"][1]:
                            await send(
                                f'Bạn không thể đặt limit phòng {value["locate"]} lớn hơn {value["limit"][1]}'
                            )

            if member and status == "kick":
                is_owner_channel = await VoiceChannels.find_one(
                    VoiceChannels.owner.discord_id == member.id,
                    VoiceChannels.vc_id == current_channel.id,
                    fetch_links=True,
                )
                if is_owner_channel:
                    await send("Bạn không thể  kick chủ phòng")
                else:
                    overwrite.connect = False
                    await current_channel.set_permissions(member, overwrite=overwrite)
                    if member in current_channel.members:
                        await member.move_to(None)
                    await send("<@" + str(member.id) + "> đã mất quyền vào phòng")

        else:
            await send("Bạn không ở trong phòng được tạo bởi Mie")
    else:
        await send("Bạn không ở trong phòng được tạo bởi Mie")


@bot.tree.command(name="clean", description="room clear")
@has_role(server_info.role_ids.admin)
async def clean(interaction: Interaction):
    await fix_room()
    await interaction.response.send_message("Fix done")


@bot.tree.command(name="public", description="Cho phép mọi người vào phòng")
async def public(interaction: Interaction):
    await room_permission(interaction, status="public")


@bot.tree.command(name="private", description="Không cho phép mọi người vào phòng")
async def private(interaction: Interaction):
    await room_permission(interaction, status="private")


@bot.tree.command(name="show", description="Hiện phòng cho mọi người thấy")
async def show(interaction: Interaction):
    await room_permission(interaction, status="show")


@bot.tree.command(name="hide", description="Ẩn phòng không cho mọi người thấy")
async def hide(interaction: Interaction):
    await room_permission(interaction, status="hide")


@bot.tree.command(name="rename", description="Đặt giới hạn phòng")
@app_commands.describe(name="Đặt lại tên phòng")
async def rename(interaction: Interaction, name: str):
    # await room_permission(interaction, name=name)
    await interaction.response.send_message(
        "Tính năng hiện tại không khả dụng. Chúng tôi sẽ thông báo khi tính năng được khôi phục."
    )


@bot.tree.command(name="limit", description="Đặt giới hạn phòng")
@app_commands.describe(limit="Đặt giới hạn phòng")
async def limit(interaction: Interaction, limit: int):
    await room_permission(interaction, limit=limit)


@bot.tree.command(name="invite", description="Mời bạn vào phòng")
@app_commands.describe()
async def invite(interaction: Interaction):
    user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

    async def user_select_callback(callback_interaction: Interaction):
        # Get member from call back interaction
        members = await asyncio.gather(
            *[
                callback_interaction.guild.fetch_member(member_id)
                for member_id in callback_interaction.data["values"]
            ]
        )

        # Set permission for members
        overwrite = discord.PermissionOverwrite()
        current_channel = interaction.user.voice.channel
        overwrite.view_channel = True
        overwrite.connect = True
        await asyncio.gather(
            *[current_channel.set_permissions(member, overwrite=overwrite) for member in members]
        )
        invite_link = await current_channel.create_invite(max_uses=1, unique=True)

        # send message to members
        try:
            await asyncio.gather(
                *[
                    member.send(
                        "**"
                        + str(interaction.user.name)
                        + "** đã mời bạn vào học: "
                        + str(invite_link)
                    )
                    for member in members
                ]
            )
        except discord.errors.HTTPException as e:
            print("Create vc invite Error: ", e)

        # send message to channel
        await callback_interaction.response.send_message(
            "Đã mời " + ",".join([f"<@{member.id}>" for member in members]) + " vào phòng"
        )

    user_select.callback = user_select_callback
    view = View(timeout=180)
    view.add_item(user_select)

    await interaction.response.send_message(view=view, delete_after=180)


@bot.tree.command(name="allow", description="Cho phép bạn vào phòng")
@app_commands.describe()
async def allow(interaction: Interaction):
    user_select = discord.ui.UserSelect(placeholder="Select", max_values=10)

    async def user_select_callback(callback_interaction: Interaction):
        # Get member from call back interaction
        members = await asyncio.gather(
            *[
                callback_interaction.guild.fetch_member(member_id)
                for member_id in callback_interaction.data["values"]
            ]
        )

        # Set permission for members
        overwrite = discord.PermissionOverwrite()
        current_channel = interaction.user.voice.channel
        overwrite.view_channel = True
        overwrite.connect = True
        await asyncio.gather(
            *[current_channel.set_permissions(member, overwrite=overwrite) for member in members]
        )

        # send message to channel
        await callback_interaction.response.send_message(
            "Đã cấp quyền cho " + ",".join([f"<@{member.id}>" for member in members]) + " vào phòng"
        )

    user_select.callback = user_select_callback
    view = View(timeout=180)
    view.add_item(user_select)

    await interaction.response.send_message(view=view, delete_after=180)


# TODO: fix this bug
@bot.tree.command(name="mute", description="Tắt mic phòng")
async def mute(interaction: Interaction):
    await room_permission(interaction, status="mute")


# TODO: fix this bug
@bot.tree.command(name="unmute", description="Mở mic phòng")
async def unmute(interaction: Interaction):
    await room_permission(interaction, status="unmute")


@bot.tree.command(name="kick", description="Kick khỏi phòng")
@app_commands.describe(member="Some one")
async def kick(interaction: Interaction, member: Union[discord.User, discord.Member]):
    await room_permission(interaction, status="kick", member=member)
