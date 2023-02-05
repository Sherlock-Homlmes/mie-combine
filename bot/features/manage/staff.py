from bot import (
    # neccess
    discord,
    bot,
    get,
    Interaction,
    app_commands,
    has_permissions,
)
from discord.app_commands import Choice

from typing import Optional


@bot.tree.command(name="add_staff", description="Quản lý nhân viên")
@app_commands.choices(
    position=[Choice(name="Leader/Manager", value=1), Choice(name="Staff", value=2)]
)
@app_commands.describe(role="Role bạn quản lý")
@app_commands.describe(member="Member")
@app_commands.default_permissions(administrator=True)
async def add_staff(
    interaction: Interaction,
    position: Optional[Choice[int]],
    role: discord.Role,
    member: discord.Member,
):

    if not position:
        position = 2

    if position.value == 1 and interaction.user.id == interaction.guild.owner_id:
        await interaction.response.send_message("You are owner")

    elif position.value == 2:
        pass
