from base import (
  # necess
  discord,bot,tasks,get,
  # var
  )
import asyncio

full_cam_id =[
915238716803514389,
915923719216574485
]
cam_stream_id = [
947404118979403796,
947404163103465512
]

@bot.listen()
async def on_voice_state_update(member, member_before, member_after):
#################check cam bot################################
  voice_channel_before = member_before.channel
  voice_channel_after = member_after.channel

  mem_id = str(member.id)
  mem_name = str(member.name)

  if member_after.channel != None:
  ###############only cam      
  ####check cam on
      if member_after.channel.id in full_cam_id:
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False:
            print("kick cam start")
            await asyncio.sleep(10)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.channel.id in full_cam_id:

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')
    
                try:
                    msg = await member.send(content=member.mention,embed=embed)
                except Exception as e:
                    print(e)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.channel.id in full_cam_id:
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')
                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick cam end")



  ###############cam | stream
  ####check cam on
      if member_after.channel.id in cam_stream_id:
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False and mem_voice_state.self_stream == False:
            print("kick stream start")
            await asyncio.sleep(10)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and mem_voice_state.channel.id in cam_stream_id:

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                try:
                    msg = await member.send(content=member.mention,embed=embed)
                except Exception as e:
                    print(e)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and mem_voice_state.channel.id in cam_stream_id:
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam/stream",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick stream end")

#################custom check cam bot################################
  ###############custom only cam      
  ####check cam on
      if member_after.channel.name.lower().startswith("full cam") :
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False:
            print("kick cam start")
            await asyncio.sleep(15)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("full cam"):

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng FULL CAM. Hãy bật camera, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')

                try:
                    msg = await member.send(content=member.mention,embed=embed)
                except Exception as e:
                    print(e)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("full cam"):
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')
                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick cam end")



  ###############custom cam | stream
  ####check cam on
      if member_after.channel.name.lower().startswith("cam stream"):
          await asyncio.sleep(5)
          mem_voice_state = member.voice
          if mem_voice_state.self_video == False and member_after.channel.name.lower().startswith("cam stream"):
            print("kick stream start")
            await asyncio.sleep(15)

            #nhắc nhở
            mem_voice_state = member.voice
            if mem_voice_state != None:
              if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and member_after.channel.name.lower().startswith("cam stream"):

                embed= discord.Embed(
                title = "**Nhắc nhở**",
                description = member.name+", bạn đang ở trong phòng CAM/STREAM. Hãy bật camera hoặc stream, nếu không bạn sẽ bị kick sau 1 phút",
                colour = discord.Colour.red()
                )
                pfp = member.avatar_url
                embed.set_thumbnail(url=pfp)
                embed.set_footer(text='''BetterMe-Better everyday''')
                
                try:
                    msg = await member.send(content=member.mention,embed=embed)
                except Exception as e:
                    print(e)

                #kick
                await asyncio.sleep(45)
                mem_voice_state = member.voice
                if mem_voice_state != None:
                  if mem_voice_state.self_video == False and mem_voice_state.self_stream == False and member_after.channel.name.lower().startswith("cam stream"):
                    await member.move_to(None)

                    embed= discord.Embed(
                    title = "**Nhắc nhở**",
                    description = member.name+", bạn đã bị kick ra khỏi phòng vì không bật cam hoặc stream",
                    colour = discord.Colour.red()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)
                  else:

                    embed= discord.Embed(
                    title = "**Cảm ơn**",
                    description = member.name+", cảm ơn bạn đã bật cam/stream",
                    colour = discord.Colour.green()
                    )
                    pfp = member.avatar_url
                    embed.set_thumbnail(url=pfp)
                    embed.set_footer(text='''BetterMe-Better everyday''')

                    await msg.edit(embed=embed)

                else:
                  embed= discord.Embed(
                      title = "**Cảm ơn**",
                      description = member.name+", cảm ơn bạn đã rời phòng",
                      colour = discord.Colour.green()
                      )
                  pfp = member.avatar_url
                  embed.set_thumbnail(url=pfp)
                  embed.set_footer(text='''BetterMe-Better everyday''')

                  await msg.edit(embed=embed)                  
            print("kick stream end")
  