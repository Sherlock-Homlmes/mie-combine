# REFACTOR
# default
import asyncio

# lib
import discord

# local
from core.conf.bot.conf import bot, server_info
from models import ErrandData, Users, VoiceChannels
from utils.discord_bot.channel_name import (
    check_avaiable_name,
)
from utils.time_modules import Now

from . import vars
from .vars import Room, all_created_vc_id

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
    global vc_id_name_map, guild, is_ready

    # if not vars.is_ready:
    #     return
    print(11111, vars.is_ready)

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

                # TODO: refactor
                if not len(voice_channel_before.members):
                    category_before_id = voice_channel_before.category.id
                    additional_category_channel_cre_id = (
                        get_additional_category_id_channel_cre_id(category_before_id)
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
                        # TODO: remove this print
                        print("-------------", e.code, e.text)
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
                            new_room_category = await server_info.guild.create_category(
                                "———("
                                + channel_info["locate"]
                                + str(len(channel_info["additional_category_ids"]) + 2)
                                + ")———"
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
                        await vc_channel.send(f"<@{member.id}>" + command_mess)

                    except discord.errors.HTTPException:
                        await asyncio.gather(
                            *[x.delete() for x in [vc_channel, data_voice_channel]]
                        )
                        all_created_vc_id.remove(vc_channel.id)
                        del vc_id_name_map[vc_channel.id]
