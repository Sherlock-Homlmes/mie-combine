# lib
import discord
import asyncio

# local
from base import bot, server_info


@bot.listen()
async def on_voice_state_update(member: discord.Member, member_before, member_after):

    full_cam_channels = server_info.full_cam_category.voice_channels
    cam_stream_channels = server_info.cam_stream_category.voice_channels
    print(
        server_info.full_cam_category,
        server_info.full_cam_category.category,
        server_info.full_cam_category.voice_channels,
        server_info.full_cam_category.text_channels,
        server_info.full_cam_category.channels,
    )

    ###only cam
    if member_after.channel in full_cam_channels:
        await asyncio.sleep(5)
        if member.voice.self_video == False:
            await asyncio.sleep(10)
            # remind
            if (
                member.voice.self_video == False
                and member.voice.channel in full_cam_channels
            ):

                embed = discord.Embed(
                    title="**Nhắc nhở**",
                    description=member.name
                    + ", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
                    colour=discord.Colour.red(),
                )
                embed.set_footer(text="""BetterMe-Better everyday""")

                try:
                    msg = await member.send(content=member.mention, embed=embed)
                except Exception as e:
                    print(e)

                # kick
                await asyncio.sleep(60)
                if member.voice != None:
                    if (
                        member.voice.self_video == False
                        and member.voice.channel in full_cam_channels
                    ):
                        await member.move_to(None)
                        title = "Nhắc nhở"
                        message = ("bạn đã bị kick ra khỏi phòng vì không bật cam",)
                        colour = discord.Colour.red()
                    else:
                        title = "Cảm ơn"
                        message = ("cảm ơn bạn đã bật cam",)
                        colour = discord.Colour.green()
                else:
                    title = ("Cảm ơn",)
                    message = (member.name + ", cảm ơn bạn đã rời phòng",)
                    colour = discord.Colour.green()

                if msg:
                    embed = discord.Embed(
                        title=f"**{title}**",
                        description=f"{member.name}, {message}",
                        colour=colour,
                    )
                    embed.set_footer(text="""BetterMe-Better everyday""")
                    await msg.edit(embed=embed)

        # ###############cam | stream
        # ####check cam on
        # if member_after.channel.id in cam_stream_ids:
        #     await asyncio.sleep(5)
        #     member.voice = member.voice
        #     if member.voice.self_video == False and member.voice.self_stream == False:
        #         print("kick stream start")
        #         await asyncio.sleep(10)

        #         # nhắc nhở
        #         member.voice = member.voice
        #         if member.voice != None:
        #             if (
        #                 member.voice.self_video == False
        #                 and member.voice.self_stream == False
        #                 and member.voice.channel.id in cam_stream_ids
        #             ):

        #                 embed = discord.Embed(
        #                     title="**Nhắc nhở**",
        #                     description=member.name
        #                     + ", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
        #                     colour=discord.Colour.red(),
        #                 )
        #                 # pfp = member.avatar_url
        #                 # embed.set_thumbnail(url=pfp)
        #                 embed.set_footer(text="""BetterMe-Better everyday""")

        #                 try:
        #                     msg = await member.send(content=member.mention, embed=embed)
        #                 except Exception as e:
        #                     print(e)

        #                 # kick
        #                 await asyncio.sleep(45)
        #                 member.voice = member.voice
        #                 if member.voice != None:
        #                     if (
        #                         member.voice.self_video == False
        #                         and member.voice.self_stream == False
        #                         and member.voice.channel.id in cam_stream_ids
        #                     ):
        #                         await member.move_to(None)

        #                         embed = discord.Embed(
        #                             title="**Nhắc nhở**",
        #                             description=member.name
        #                             + ", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
        #                             colour=discord.Colour.red(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")

        #                         await msg.edit(embed=embed)
        #                     else:

        #                         embed = discord.Embed(
        #                             title="**Cảm ơn**",
        #                             description=member.name
        #                             + ", cảm ơn bạn đã bật cam/stream",
        #                             colour=discord.Colour.green(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")

        #                         await msg.edit(embed=embed)

        #                 else:
        #                     embed = discord.Embed(
        #                         title="**Cảm ơn**",
        #                         description=member.name + ", cảm ơn bạn đã rời phòng",
        #                         colour=discord.Colour.green(),
        #                     )
        #                     # pfp = member.avatar_url
        #                     # embed.set_thumbnail(url=pfp)
        #                     embed.set_footer(text="""BetterMe-Better everyday""")

        #                     await msg.edit(embed=embed)
        #         print("kick stream end")

        # #################custom check cam bot################################
        # ###############custom only cam
        # ####check cam on
        # if member_after.channel.name.lower().startswith("full cam"):
        #     await asyncio.sleep(5)
        #     member.voice = member.voice
        #     if member.voice.self_video == False:
        #         print("kick cam start")
        #         await asyncio.sleep(15)

        #         # nhắc nhở
        #         member.voice = member.voice
        #         if member.voice != None:
        #             if (
        #                 member.voice.self_video == False
        #                 and member_after.channel.name.lower().startswith("full cam")
        #             ):

        #                 embed = discord.Embed(
        #                     title="**Nhắc nhở**",
        #                     description=member.name
        #                     + ", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
        #                     colour=discord.Colour.red(),
        #                 )
        #                 # pfp = member.avatar_url
        #                 # embed.set_thumbnail(url=pfp)
        #                 embed.set_footer(text="""BetterMe-Better everyday""")

        #                 try:
        #                     msg = await member.send(content=member.mention, embed=embed)
        #                 except Exception as e:
        #                     print(e)

        #                 # kick
        #                 await asyncio.sleep(45)
        #                 member.voice = member.voice
        #                 if member.voice != None:
        #                     if (
        #                         member.voice.self_video == False
        #                         and member_after.channel.name.lower().startswith(
        #                             "full cam"
        #                         )
        #                     ):
        #                         await member.move_to(None)

        #                         embed = discord.Embed(
        #                             title="**Nhắc nhở**",
        #                             description=member.name
        #                             + ", bạn đã bị kick ra khỏi phòng vì không bật cam",
        #                             colour=discord.Colour.red(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")
        #                         await msg.edit(embed=embed)
        #                     else:

        #                         embed = discord.Embed(
        #                             title="**Cảm ơn**",
        #                             description=member.name + ", cảm ơn bạn đã bật cam",
        #                             colour=discord.Colour.green(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")

        #                         await msg.edit(embed=embed)

        #                 else:
        #                     embed = discord.Embed(
        #                         title="**Cảm ơn**",
        #                         description=member.name + ", cảm ơn bạn đã rời phòng",
        #                         colour=discord.Colour.green(),
        #                     )
        #                     # pfp = member.avatar_url
        #                     # embed.set_thumbnail(url=pfp)
        #                     embed.set_footer(text="""BetterMe-Better everyday""")

        #                     await msg.edit(embed=embed)
        #         print("kick cam end")

        # ###############custom cam | stream
        # ####check cam on
        # if member_after.channel.name.lower().startswith("cam stream"):
        #     await asyncio.sleep(5)
        #     member.voice = member.voice
        #     if (
        #         member.voice.self_video == False
        #         and member_after.channel.name.lower().startswith("cam stream")
        #     ):
        #         print("kick stream start")
        #         await asyncio.sleep(15)

        #         # nhắc nhở
        #         member.voice = member.voice
        #         if member.voice != None:
        #             if (
        #                 member.voice.self_video == False
        #                 and member.voice.self_stream == False
        #                 and member_after.channel.name.lower().startswith("cam stream")
        #             ):

        #                 embed = discord.Embed(
        #                     title="**Nhắc nhở**",
        #                     description=member.name
        #                     + ", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
        #                     colour=discord.Colour.red(),
        #                 )
        #                 # pfp = member.avatar_url
        #                 # embed.set_thumbnail(url=pfp)
        #                 embed.set_footer(text="""BetterMe-Better everyday""")

        #                 try:
        #                     msg = await member.send(content=member.mention, embed=embed)
        #                 except Exception as e:
        #                     print(e)

        #                 # kick
        #                 await asyncio.sleep(45)
        #                 member.voice = member.voice
        #                 if member.voice != None:
        #                     if (
        #                         member.voice.self_video == False
        #                         and member.voice.self_stream == False
        #                         and member_after.channel.name.lower().startswith(
        #                             "cam stream"
        #                         )
        #                     ):
        #                         await member.move_to(None)

        #                         embed = discord.Embed(
        #                             title="**Nhắc nhở**",
        #                             description=member.name
        #                             + ", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
        #                             colour=discord.Colour.red(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")

        #                         await msg.edit(embed=embed)
        #                     else:

        #                         embed = discord.Embed(
        #                             title="**Cảm ơn**",
        #                             description=member.name
        #                             + ", cảm ơn bạn đã bật cam/stream",
        #                             colour=discord.Colour.green(),
        #                         )
        #                         # pfp = member.avatar_url
        #                         # embed.set_thumbnail(url=pfp)
        #                         embed.set_footer(text="""BetterMe-Better everyday""")

        #                         await msg.edit(embed=embed)

        #                 else:
        #                     embed = discord.Embed(
        #                         title="**Cảm ơn**",
        #                         description=member.name + ", cảm ơn bạn đã rời phòng",
        #                         colour=discord.Colour.green(),
        #                     )
        #                     # pfp = member.avatar_url
        #                     # embed.set_thumbnail(url=pfp)
        #                     embed.set_footer(text="""BetterMe-Better everyday""")

        #                     await msg.edit(embed=embed)
        #         print("kick stream end")
