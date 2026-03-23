# default
import asyncio

# lib
import discord

# local
from core.conf.bot.conf import bot, server_info

welcome_member = []


@bot.listen()
async def on_member_join(member: discord.Member):
    global welcome_member

    await bot._fully_ready.wait()

    if member.id not in welcome_member:
        embed = discord.Embed(
            title="**Chào mừng "
            + member.name
            + " đến với Cộng Đồng học tập BetterMe**",
            description=" Hãy giới thiệu bản thân cho mọi người biết ở <#894594032947310602> nhé",
            colour=discord.Colour.gold(),
        )

        if member.avatar:
            pfp = member.avatar.url
        else:
            pfp = member.default_avatar.url
        field1 = "Hãy đọc kĩ luật ở <#880369537449619476> nha"
        field3 = "Hãy vào **Channels & Roles** (phía góc trái trên) để nhận role tương ứng nha"
        field2 = "Nếu bạn có thắc mắc thì cứ hỏi bọn mình nha <#1024083239486377995>"

        embed.set_footer(
            text="""Chúc bạn có 1 khoảng thời gian vui vẻ.
  BetterMe-Better everyday"""
        )
        embed.set_image(url="https://i.ibb.co/bNzBtyY/Betterme-banner.png")
        embed.set_thumbnail(url=pfp)
        embed.add_field(name="**Đọc kĩ luật**", value=field1, inline=False)
        embed.add_field(name="**Hướng dẫn cơ bản**", value=field2, inline=False)
        embed.add_field(name="**Set role**", value=field3, inline=False)

        msg = await server_info.welcome_channel.send(
            content=member.mention, embed=embed
        )
        welcome_member.append(member.id)
        await asyncio.sleep(600)
        await msg.delete()
        welcome_member.remove(member.id)
