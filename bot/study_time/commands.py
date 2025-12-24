# default
import asyncio

# lib
import discord

# local
from core.conf.bot.conf import bot, server_info
from core.models import Users
from .study_time_log import update_user_monthly_role


@bot.tree.command(
    name="disable_achievement_role", description="Vô hiệu hóa Achievement role"
)
async def disable_achievement_role(interaction: discord.Interaction):
    author = interaction.user
    all_achivement_role_ids = [
        server_info.role_ids.iron,
        server_info.role_ids.bronze,
        server_info.role_ids.silver,
        server_info.role_ids.gold,
        server_info.role_ids.diamond,
        server_info.role_ids.master,
        server_info.role_ids.challenger,
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


@bot.tree.command(
    name="enable_achievement_role", description="Kích hoạt Achievement role"
)
async def enable_achievement_role(interaction: discord.Interaction):
    author = interaction.user

    author_db = await Users.find_one({"discord_id": author.id})
    author_db.update_metadata({"disable_achievement_role": False})

    await asyncio.gather(
        *[
            author_db.save(),
            update_user_monthly_role(author),
            interaction.response.send_message("Đã kích hoạt Achievement role."),
        ]
    )
