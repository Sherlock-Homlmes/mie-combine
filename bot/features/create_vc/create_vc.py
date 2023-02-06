# default
import asyncio
from typing import Optional, Union

# lib
import discord
from discord import Interaction, app_commands
from discord.ext.commands import has_role
from discord.errors import NotFound


# local
from bot import bot, server_info
from models import VoiceChannels, Users

from other_modules.discord_bot.channel_name import (
    check_avaiable_name,
    rewrite_create_voice_channel_name,
)


command_mess = """
**Các lệnh:**
```
/public: mở phòng cho tất cả mọi người vào

/private: khóa phòng, chỉ những người được mời mới vào được

/hide: ẩn phòng với mọi người

/show: hiện phòng với mọi người

/mute: tắt âm phòng

/unmute: bỏ tắt âm phòng

/allow + [tên_người_muốn_mời hoặc id]: cho phép người bạn muốn vào phòng

/invite + [tên_người_muốn_mời hoặc id]: mời người vào phòng

/kick + [tên_người_muốn_kick hoặc id]: kick ra khỏi phòng

/limit + [số_người_giới_hạn]

/rename + [tên phòng]: đổi tên phòng

```

***Chú ý:**
-Bạn chỉ có thể tạo 1 phòng cùng lúc
-Phòng chat này chỉ những người đang trong phòng của bạn mới thấy
-Phòng sẽ mất khi không còn ai trong phòng
-Bạn có thể gọi bot trong kênh này
||Chúc bạn học vui :3||
"""


# ----------START-----------
all_created_vc_id = []


@bot.listen()
async def on_ready():
    global all_created_vc_id

    print("6.Create voice channel ready")
    await asyncio.sleep(10)
    # get all created voice channel
    voice_channels = await VoiceChannels.find({}).to_list()
    all_created_vc_id = [int(voice_channel.vc_id) for voice_channel in voice_channels]

    # delete empty voice channel
    await fix_room()


async def fix_room():
    global all_created_vc_id

    for vc_id in all_created_vc_id:
        try:
            vc_channel = await server_info.guild.fetch_channel(vc_id)
        except:
            vc_channel = None

        if vc_channel:
            if vc_channel.members == []:
                await vc_channel.delete()
                vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
                try:
                    cc_channel = await server_info.guild.fetch_channel(vc.cc_id)
                except:
                    cc_channel = None
                if cc_channel:
                    await cc_channel.delete()
                await vc.delete()
        else:
            vc = await VoiceChannels.find_one(VoiceChannels.vc_id == vc_id)
            try:
                cc_channel = await server_info.guild.fetch_channel(vc.cc_id)
            except:
                cc_channel = None
            if cc_channel:
                await cc_channel.delete()
            await vc.delete()

    print("fix done")


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    global all_created_vc_id

    ##################### create-voice-channel #####################
    voice_channel_before = member_before.channel
    voice_channel_after = member_after.channel

    # thứ tự: mem out -> mem in -> cre
    if voice_channel_after != voice_channel_before:

        ##member out
        if voice_channel_before != None:
            if voice_channel_before.id in all_created_vc_id:
                await asyncio.sleep(5)
                vc = await VoiceChannels.find_one(
                    VoiceChannels.vc_id == voice_channel_before.id
                )

                if voice_channel_before.members == []:
                    channel_del = server_info.guild.get_channel(vc.vc_id)
                    if channel_del:
                        await channel_del.delete()
                    channel_del = server_info.guild.get_channel(vc.cc_id)
                    if channel_del != None:
                        await channel_del.delete()

                    await vc.delete()
                    all_created_vc_id.remove(voice_channel_before.id)

                elif not member.bot:
                    cc_channel = server_info.guild.get_channel(vc.cc_id)
                    await cc_channel.set_permissions(member, overwrite=None)

        ###member in
        if voice_channel_after != None:
            # set member's permission to text channel
            if voice_channel_after.id in all_created_vc_id:
                await asyncio.sleep(3)
                vc = await VoiceChannels.find_one(
                    VoiceChannels.vc_id == voice_channel_after.id
                )
                cc_channel = server_info.guild.get_channel(vc.cc_id)
                overwrite = discord.PermissionOverwrite()
                overwrite.view_channel = True
                await cc_channel.set_permissions(member, overwrite=overwrite)

            ## create channel + set role
            elif str(voice_channel_after.id) in server_info.channel_cre.keys():
                if check_avaiable_name(member.name) == False:
                    await member.move_to(None)
                    await member.send(
                        "**Bạn hãy kiểm tra và đảm bảo trong tên của bạn không có từ cấm, tục tĩu**"
                    )
                else:
                    channel_info = server_info.channel_cre[str(voice_channel_after.id)]
                    category_id = channel_info["category_id"]
                    lim = channel_info["limit"]
                    category = await server_info.guild.fetch_channel(category_id)

                    ##### create
                    cc_name = rewrite_create_voice_channel_name(member.name)
                    vc_name = f"#{cc_name}'s room"
                    vc_channel = await category.create_voice_channel(vc_name)
                    all_created_vc_id.append(vc_channel.id)
                    await member.move_to(vc_channel)
                    cc_channel = await category.create_text_channel(cc_name)

                    await VoiceChannels(
                        owner=await Users.find_one(Users.discord_id == str(member.id)),
                        cc_id=cc_channel.id,
                        vc_id=vc_channel.id,
                    ).insert()
                    #####set permission
                    overwrite = discord.PermissionOverwrite()

                    # everyone
                    overwrite.connect = False
                    everyone_role = server_info.guild.get_role(server_info.guild.id)
                    await vc_channel.set_permissions(everyone_role, overwrite=overwrite)
                    overwrite.view_channel = False
                    await cc_channel.set_permissions(everyone_role, overwrite=overwrite)
                    # user
                    overwrite.view_channel = True
                    overwrite.connect = True
                    await cc_channel.set_permissions(member, overwrite=overwrite)
                    await vc_channel.set_permissions(member, overwrite=overwrite)
                    # bot
                    bot_role = server_info.guild.get_role(
                        server_info.feature_bot_role_id
                    )
                    overwrite.send_messages = True
                    await cc_channel.set_permissions(bot_role, overwrite=overwrite)
                    await vc_channel.set_permissions(bot_role, overwrite=overwrite)
                    await vc_channel.edit(user_limit=lim[1])
                    await cc_channel.send(f"<@{member.id}>" + command_mess)


### slash command
async def room_permission(
    interaction: Interaction,
    status: Optional[str] = None,
    name: Optional[str] = None,
    limit: Optional[int] = None,
    member: Optional[Union[discord.User, discord.Member]] = None,
):
    current_channel = interaction.user.voice.channel
    send = interaction.response.send_message

    if current_channel:
        if current_channel.id in all_created_vc_id:
            vc_channel = server_info.guild.get_channel(current_channel.id)

            if status in ["public", "private", "show", "hide", "mute", "unmute"]:
                overwrite = discord.PermissionOverwrite()

                if status == "public":
                    overwrite.connect = True
                    message = "Phòng đã được mở cho mọi người vào"
                elif status == "private":
                    overwrite.connect = False
                    message = "Phòng đã được đóng cho mọi người vào"
                elif status == "show":
                    overwrite.view_channel = True
                    message = "Phòng đã được hiện cho mọi người thấy"
                elif status == "hide":
                    overwrite.view_channel = False
                    message = "Phòng đã được ẩn không cho mọi người thấy"
                elif status == "mute":
                    overwrite.speak = False
                    message = "Đã tắt âm phòng"
                elif status == "unmute":
                    overwrite.speak = True
                    message = "Đã bỏ tắt âm phòng"

                everyone_role = server_info.guild.get_role(server_info.guild.id)
                await vc_channel.set_permissions(everyone_role, overwrite=overwrite)
                await send(message)

            if name:
                if check_avaiable_name(name):
                    new_name = name
                    if len(new_name) > 50:
                        await send("Tên quá dài")
                    else:
                        await vc_channel.edit(name=new_name)
                        await send("Tên kênh đã được đổi thành " + new_name)
                else:
                    await send(
                        "**Không được đổi tên kênh có những từ cấm nha mầy, tau táng cho á**"
                    )

            if limit:
                category_id = interaction.channel.category.id
                for key, value in server_info.channel_cre.items():
                    if value["category_id"] == category_id:
                        if value["limit"][0] == value["limit"][1]:
                            await send(
                                "Bạn không thể đặt limit cho phòng " + value["locate"]
                            )
                        elif limit >= value["limit"][0] and limit <= value["limit"][1]:
                            await vc_channel.edit(user_limit=limit)
                            await send(f"**Đã đặt limit cho phòng:** {limit}")
                        elif limit < value["limit"][0]:
                            await send(
                                f'Bạn không thể đặt limit phòng {value["locate"]} bé hơn {value["limit"][0]}'
                            )
                        elif limit > value["limit"][1]:
                            await send(
                                f'Bạn không thể đặt limit phòng {value["locate"]} lớn hơn {value["limit"][1]}'
                            )

            if member:
                overwrite = discord.PermissionOverwrite()
                if status == "invite":
                    overwrite.view_channel = True
                    overwrite.connect = True
                    await vc_channel.set_permissions(member, overwrite=overwrite)
                    invite_link = await vc_channel.create_invite(
                        max_uses=1, unique=True
                    )
                    await member.send(
                        "**"
                        + str(interaction.user.name)
                        + "** đã mời bạn vào học: "
                        + str(invite_link)
                    )
                    await send("Đã mời <@" + str(member.id) + "> vào phòng")
                elif status == "allow":
                    overwrite.view_channel = True
                    overwrite.connect = True
                    await vc_channel.set_permissions(member, overwrite=overwrite)
                    await send("Đã cấp quyền cho <@" + str(member.id) + "> vào phòng")
                elif status == "kick":
                    overwrite.connect = False
                    await vc_channel.set_permissions(member, overwrite=overwrite)
                    await send("<@" + str(member.id) + "> đã mất quyền vào phòng")
                    if member in vc_channel.members:
                        await member.move_to(None)

        else:
            await send("Bạn không ở trong phòng được tạo bởi Mie")
    else:
        await send("Bạn không ở trong phòng được tạo bởi Mie")


@bot.tree.command(name="clean", description="room clear")
@has_role(server_info.admin_role_id)
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
async def private(interaction: Interaction):
    await room_permission(interaction, status="show")


@bot.tree.command(name="hide", description="Ẩn phòng không cho mọi người thấy")
async def private(interaction: Interaction):
    await room_permission(interaction, status="hide")


@bot.tree.command(name="rename", description="Đặt giới hạn phòng")
@app_commands.describe(name="Đặt lại tên phòng")
async def rename(interaction: Interaction, name: str):
    await room_permission(interaction, name=name)


@bot.tree.command(name="limit", description="Đặt giới hạn phòng")
@app_commands.describe(limit="Đặt giới hạn phòng")
async def limit(interaction: Interaction, limit: int):
    await room_permission(interaction, limit=limit)


@bot.tree.command(name="invite", description="Mời bạn vào phòng")
@app_commands.describe(member="Some one")
async def invite(interaction: Interaction, member: Union[discord.User, discord.Member]):
    if member:
        await room_permission(interaction, status="invite", member=member)
    else:
        await interaction.response.send_message("Không tìm thấy người dùng")


@bot.tree.command(name="allow", description="Cho phép bạn vào phòng")
@app_commands.describe(member="Some one")
async def allow(interaction: Interaction, member: Union[discord.User, discord.Member]):
    if member:
        await room_permission(interaction, status="allow", member=member)
    else:
        await interaction.response.send_message("Không tìm thấy người dùng")


@bot.tree.command(name="mute", description="Tắt âm phòng")
async def private(interaction: Interaction):
    await room_permission(interaction, status="mute")


@bot.tree.command(name="unmute", description="Mở âm phòng")
async def private(interaction: Interaction):
    await room_permission(interaction, status="unmute")


@bot.tree.command(name="kick", description="Kick khỏi phòng")
@app_commands.describe(member="Some one")
async def kick(interaction: Interaction, member: Union[discord.User, discord.Member]):
    await room_permission(interaction, status="kick", member=member)