# default
import asyncio

# lib
import discord
from discord.ext import commands

# local
from core.conf.bot.conf import server_info


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_member = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Welcome module ready")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot._fully_ready.wait()

        if member.id not in self.welcome_member:
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
            field2 = (
                "Nếu bạn có thắc mắc thì cứ hỏi bọn mình nha <#1024083239486377995>"
            )

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
            self.welcome_member.append(member.id)
            await asyncio.sleep(600)
            await msg.delete()
            self.welcome_member.remove(member.id)


async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
