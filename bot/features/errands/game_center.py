# default
import asyncio

# lib
import discord
from discord import Interaction

# local
from bot import bot, server_info


@bot.listen()
async def on_interaction(interaction: Interaction):
    global khu_vui_choi, game_center_interaction_id

    ####game
    if interaction.message:
        if (
            interaction.message.id == game_center_interaction_id
            and interaction.type == discord.InteractionType.component
        ):
            game_roles = server_info.game_roles
            kvc_role = server_info.guild.get_role(game_roles["game_center"])
            values = interaction.data["values"]

            if "none game" in values:
                for key in game_roles.keys():
                    server_info.guild.get_role(game_roles[key])
                    await interaction.user.remove_roles(role)

                await interaction.user.remove_roles(kvc_role)

                msg = await interaction.message.channel.send(
                    f"**{interaction.user.mention} đã chọn không chơi game**"
                )

            elif "game all" in values or set(list(game_roles.keys())) == set(values):
                await interaction.user.add_roles(kvc_role)

                for key in game_roles.keys():
                    role = discord.utils.get(
                        interaction.guild.roles, id=game_roles[key]
                    )
                    await interaction.user.remove_roles(role)

                msg = await interaction.message.channel.send(
                    f"**{interaction.user.mention} đã chọn chơi tất cả mọi game**"
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
                    f"**{interaction.user.mention} đã chọn chơi: " + game + "**"
                )

            await interaction.response.defer()
            await asyncio.sleep(10)
            await msg.delete()
