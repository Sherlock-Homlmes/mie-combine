# default
from discord import app_commands, Interaction

# local
from bot import bot, server_info


@bot.tree.command(name="color", description="Đổi màu cho tên")
@app_commands.describe(number="Số thứ tự của màu")
async def limit(interaction: Interaction, number: int):

    if number > len(server_info.color_roles):
        await interaction.response.send_message("Chọn sai số màu")
    else:
        user = interaction.user
        role_names = [role.name for role in user.roles]
        if "HOMIE" in role_names or "HỌC SINH TÍCH CỰC" in role_names:
            if "COLOR" in role_names:
                pos = role_names.index("COLOR")
                role_ids = [role.id for role in user.roles]
                color_old = server_info.guild.get_role(role_ids[pos])
                await user.remove_roles(color_old)

            color_new = server_info.guild.get_role(server_info.color_roles[number - 1])
            await user.add_roles(color_new)
            await interaction.response.send_message(
                f"Bạn đã đổi sang màu **{number}** thành công"
            )

        else:
            await interaction.response.send_message(
                "Bạn chưa có role HOMIE hoặc HSTC để đổi màu"
            )


@bot.tree.command(name="rmcolor", description="Loại bỏ mảu khỏi tên")
async def color(interaction: Interaction):
    user = interaction.user
    role_names = [role.name for role in user.roles]
    if "COLOR" in role_names:
        pos = role_names.index("COLOR")
        role_ids = [role.id for role in user.roles]
        color_old = server_info.guild.get_role(role_ids[pos])
        await user.remove_roles(color_old)
    await interaction.response.send_message("Bạn đã bỏ role màu")
