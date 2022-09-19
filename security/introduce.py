from base import (
  # necess
  discord,bot,tasks,get,
  # var
  )


@bot.listen()
async def on_message(message):
  if str(message.channel) == "giới-thiệu-bản-thân" and message.author.bot == False and len(message.content) <120 :
    await message.delete()
    embed= discord.Embed(
    title = "**Chào mừng "+message.author.name+" đến với Cộng Đồng học tập BetterMe**",
    description ="Bạn giới thiệu đầy đủ 1 xíu nha.",
    colour = discord.Colour.gold()
    )
    basic = '''
      Tên tuổi
      Năm sinh
      Nơi ở
      Sở thích cá nhân
      Điểm mạnh, yếu
      Mục tiêu trong tương lai
      ...
      ||**Trên 120 từ nhé :3**||
    '''
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.add_field(name="**Một mẫu giới thiệu cơ bản**",value=basic,inline=False)
    await message.author.send(embed = embed)
