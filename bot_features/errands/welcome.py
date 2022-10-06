from base import (
    # necess
    discord,bot,
    get,
    # var
    channel_cre)
import asyncio

welcome_member = []

@bot.listen()
async def on_member_join(member):
  global welcome_member
  
  if member.id not in welcome_member:
    embed= discord.Embed(
    title = "**Chào mừng "+member.name+" đến với Cộng Đồng học tập BetterMe**",
    description =" Hãy giới thiệu bản thân cho mọi người biết ở <#894594032947310602> nhé",
    colour = discord.Colour.gold()
    )

    welcome_channel = get(member.guild.channels, id=894594032947310602)

    pfp = member.avatar.url
    field1="Hãy đọc kĩ luật ở <#880369537449619476> nha"
    field2="Nếu bạn chưa biết cách dùng Discord thì ở <#915949063403347968> có đó"
    field3="Hãy vào <#891909866355048548> để nhận role tương ứng nha"

    embed.set_footer(text='''Chúc bạn có 1 khoảng thời gian vui vẻ. 
  BetterMe-Better everyday''')
    embed.set_image(url="https://i.ibb.co/bNzBtyY/Betterme-banner.png")
    embed.set_thumbnail(url=pfp)
    embed.add_field(name="**Đọc kĩ luật**",value=field1,inline=False)
    embed.add_field(name="**Hướng dẫn cơ bản**",value=field2,inline=False)
    embed.add_field(name="**Set role**",value=field3,inline=False)
    
    msg = await welcome_channel.send(content=member.mention,embed=embed)
    welcome_member.append(member.id)
    await asyncio.sleep(600)
    await msg.delete()
    welcome_member.remove(member.id)

@bot.listen()
async def on_message(message):
  global i,store,new_mem
  if message.author == bot.user:
    return

  if str(message.channel)== "giới-thiệu-bản-thân" and len(message.content) <120 :
    await message.delete()
    embed= discord.Embed(
    title = "**Chào mừng "+message.author.name+" đến với Cộng Đồng học tập BetterMe**",
    description ="Bạn giới thiệu đầy đủ 1 xíu nha.",
    colour = discord.Colour.gold()
    )
    coban = '''
Tên tuổi
Năm sinh
Nơi ở
Sở thích cá nhân
Điểm mạnh, yếu
Mục tiêu trong tương lai
...
||**Trên 120 từ nhé :3**||
'''
    embed.set_thumbnail(url=message.author.avatar.url)
    embed.add_field(name="**Một mẫu giới thiệu cơ bản**",value=coban,inline=False)
    await message.author.send(embed = embed)


  await bot.process_commands(message)
