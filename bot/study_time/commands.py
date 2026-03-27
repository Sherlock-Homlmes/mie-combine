# default
import asyncio

# lib
import discord
from discord import app_commands
from discord.ext import commands

# local
from core.conf.bot.conf import server_info
from models import Users

from .study_time_log import (
    update_user_monthly_role,
    update_user_positive_student_role,
)


class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Study time commands module ready")

    @app_commands.command(
        name="disable_achievement_role", description="Vô hiệu hóa Achievement role"
    )
    async def disable_achievement_role(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Vào server mà gõ. Không gõ ở đây được."
            )
            return
        author = interaction.user
        all_achivement_role_ids = [
            server_info.role_ids.iron,
            server_info.role_ids.bronze,
            server_info.role_ids.silver,
            server_info.role_ids.gold,
            server_info.role_ids.diamond,
            server_info.role_ids.master,
            server_info.role_ids.challenger,
            server_info.role_ids.positive_student,
        ]

        author_db = await Users.find_one({"discord_id": author.id})
        author_db.update_metadata({"disable_achievement_role": True})
        await author_db.save()

        for role in author.roles:
            if role.id in all_achivement_role_ids:
                await author.remove_roles(role)

        await interaction.response.send_message(
            "Đã vô hiệu hóa Achievement role. Bạn có thể bật Achievement role bằng lệnh **/enable_achievement_role** bất cứ lúc nào"
        )

    @app_commands.command(
        name="enable_achievement_role", description="Kích hoạt Achievement role"
    )
    async def enable_achievement_role(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Vào server mà gõ. Không gõ ở đây được."
            )
            return
        author = interaction.user

        author_db = await Users.find_one({"discord_id": author.id})
        author_db.update_metadata({"disable_achievement_role": False})

        await asyncio.gather(
            *[
                author_db.save(),
                update_user_positive_student_role(author, should_send_message=False),
                update_user_monthly_role(author),
                interaction.response.send_message("Đã kích hoạt Achievement role."),
            ]
        )


async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
