import os
import asyncio

from base import (
    # necess
    discord,
    bot,
    tasks,
    get,
    Interaction,
    # var
    admin_id,
    khu_vui_choi,
)
from other_modules.stable_json import open_database, write_database, fix_database

database_directory = "/game_center/game_center"
fix_database(database_directory)

game_roles = open_database(database_directory)
game_center_interaction_id = open_database("/general/general")[
    "game_center_interaction_id"
]


@bot.listen()
async def on_interaction(interaction: Interaction):
    global khu_vui_choi, game_roles, game_center_interaction_id

    ####game
    if interaction.message:
        if (
            interaction.message.id == game_center_interaction_id
            and interaction.type == discord.InteractionType.component
        ):

            kvc_role = discord.utils.get(interaction.guild.roles, id=khu_vui_choi)

            values = interaction.data["values"]

            if "none game" in values:
                for key in game_roles.keys():
                    role = discord.utils.get(
                        interaction.guild.roles, id=game_roles[key]
                    )
                    await interaction.user.remove_roles(role)

                await interaction.user.remove_roles(kvc_role)

                msg = await interaction.message.channel.send(
                    "**" + interaction.user.mention + " đã chọn không chơi game**"
                )

            elif "game all" in values or set(list(game_roles.keys())) == set(values):
                await interaction.user.add_roles(kvc_role)

                for key in game_roles.keys():
                    role = discord.utils.get(
                        interaction.guild.roles, id=game_roles[key]
                    )
                    await interaction.user.remove_roles(role)

                msg = await interaction.message.channel.send(
                    "**" + interaction.user.mention + " đã chọn chơi tất cả mọi game**"
                )

            else:
                await interaction.user.remove_roles(kvc_role)

                game = ""
                for key in values:
                    role = discord.utils.get(
                        interaction.guild.roles, id=game_roles[key]
                    )
                    await interaction.user.add_roles(role)
                    game += key + ","

                game = game.rstrip(game[-1])
                msg = await interaction.message.channel.send(
                    "**" + interaction.user.mention + " đã chọn chơi: " + game + "**"
                )

            await interaction.response.defer()
            await asyncio.sleep(10)
            await msg.delete()
