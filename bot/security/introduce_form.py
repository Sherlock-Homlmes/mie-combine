# default
# lib
import discord
from discord.ext import commands


class IntroduceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Introduce module ready")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if str(message.channel) == "giới-thiệu-bản-thân" and not message.author.bot:
            if len(message.content) < 120:
                await message.delete()
                embed = discord.Embed(
                    title="**Chào mừng "
                    + message.author.name
                    + " đến với Cộng Đồng học tập BetterMe**",
                    description="Bạn giới thiệu đầy đủ 1 xíu nha.",
                    colour=discord.Colour.gold(),
                )
                basic = """
        Tên tuổi
        Năm sinh
        Nơi ở
        Sở thích cá nhân
        Điểm mạnh, yếu
        Mục tiêu trong tương lai
        ...
        ||**Trên 120 từ nhé :3**||
        """
                embed.set_thumbnail(url=message.author.avatar.url)
                embed.add_field(
                    name="**Một mẫu giới thiệu cơ bản**", value=basic, inline=False
                )
                await message.author.send(embed=embed)

            else:
                await message.create_thread(
                    name="Mọi người vào chào bạn mới đi nào!",
                    auto_archive_duration=10080,
                )


async def setup(bot):
    await bot.add_cog(IntroduceCog(bot))
