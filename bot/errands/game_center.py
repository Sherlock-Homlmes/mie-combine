# default
import asyncio

# lib
import discord
from discord import Interaction

# local
from core.conf.bot.conf import bot, server_info, guild_id


@bot.listen()
async def on_interaction(interaction: Interaction):
    if interaction.message:
        if (
            interaction.message.id == server_info.game_center_interaction_id
            and interaction.type == discord.InteractionType.component
        ):
            game_roles = server_info.game_roles
            guild = bot.get_guild(guild_id)
            kvc_role = guild.get_role(game_roles["game_center"])
            values = interaction.data["values"]

            if "none game" in values:
                for key in game_roles.keys():
                    role = server_info.guild.get_role(game_roles[key])
                    await interaction.user.remove_roles(role)

                await interaction.user.remove_roles(kvc_role)

                msg = await interaction.message.channel.send(
                    f"**{interaction.user.mention} đã chọn không chơi game**"
                )

            elif "game all" in values or set(list(game_roles.keys())) == set(values):
                for key in game_roles.keys():
                    role = server_info.guild.get_role(game_roles[key])
                    await interaction.user.remove_roles(role)

                await interaction.user.add_roles(kvc_role)

                msg = await interaction.message.channel.send(
                    f"**{interaction.user.mention} đã chọn chơi tất cả mọi game**"
                )

            else:
                await interaction.user.remove_roles(kvc_role)

                for key in values:
                    role = discord.utils.get(interaction.guild.roles, id=game_roles[key])
                    await interaction.user.add_roles(role)
                game = ",".join(values)

                msg = await interaction.message.channel.send(
                    f"**{interaction.user.mention} đã chọn chơi: {game}**"
                )

            await asyncio.sleep(10)
            await msg.delete()
