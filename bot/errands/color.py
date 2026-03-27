# libs
from discord import Interaction, Role, User, app_commands
from discord.ext import commands

# local
from core.conf.bot.conf import server_info


class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Errand - Color module ready")

    async def remove_color_role_from_user(
        self, role_names: list[Role], user: User
    ) -> None:
        if "COLOR" in role_names:
            pos = role_names.index("COLOR")
            role_ids = [role.id for role in user.roles]
            color_old = server_info.guild.get_role(role_ids[pos])
            await user.remove_roles(color_old)

    # REFACTOR: CHANGE TO DISCORD.UI.ROLESELECT
    @app_commands.command(name="color", description="Đổi màu cho tên")
    @app_commands.describe(number="Số thứ tự của màu")
    async def color(self, interaction: Interaction, number: int):
        if number <= 0 or number > len(server_info.color_roles):
            await interaction.response.send_message("Chọn sai số màu")
        else:
            user = interaction.user
            role_names = [role.name for role in user.roles]
            if "HOMIE" in role_names or "HỌC SINH TÍCH CỰC" in role_names:
                await self.remove_color_role_from_user(role_names=role_names, user=user)
                color_new = server_info.guild.get_role(
                    server_info.color_roles[number - 1]
                )
                await user.add_roles(color_new)
                await interaction.response.send_message(
                    f"Bạn đã đổi sang màu **{number}** thành công"
                )

            else:
                await interaction.response.send_message(
                    "Bạn chưa có role HOMIE hoặc HSTC để đổi màu"
                )

    @app_commands.command(name="rmcolor", description="Loại bỏ màu khỏi tên")
    async def rmcolor(self, interaction: Interaction):
        user = interaction.user
        role_names = [role.name for role in user.roles]
        await self.remove_color_role_from_user(role_names=role_names, user=user)
        await interaction.response.send_message("Bạn đã bỏ role màu")


async def setup(bot):
    await bot.add_cog(ColorCog(bot))
