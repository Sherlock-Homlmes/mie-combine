from discord_components import DiscordComponents, Select, SelectOption, Button, ButtonStyle
import os
import asyncio

from base import (
  # necess
  discord,bot,tasks,get,
  # var
  admin_id,khu_vui_choi
)
from feature_func.stable_json import open_database, write_database, fix_database
database_directory = "/game_center/game_center"
fix_database(database_directory)

game_roles = open_database(database_directory)
game_center_interaction_id = open_database("/general/general")["game_center_interaction_id"]

@bot.listen()
async def on_select_option(interaction):
  global khu_vui_choi,game_roles, game_center_interaction_id

####game
  if interaction.message.id == game_center_interaction_id: #Message id(not obligatory)
    await interaction.respond(type=6)

    kvc_role = discord.utils.get(interaction.guild.roles, id=khu_vui_choi)

    if "none game" in interaction.values:
      for key in game_roles.keys():
        role = discord.utils.get(interaction.guild.roles, id=game_roles[key])
        await interaction.author.remove_roles(role)

      await interaction.author.remove_roles(kvc_role)

      msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn không chơi game**")    

    elif "game all" in interaction.values or set(list(game_roles.keys())) == set(interaction.values):
      await interaction.author.add_roles(kvc_role)

      for key in game_roles.keys():
        role = discord.utils.get(interaction.guild.roles, id=game_roles[key])
        await interaction.author.remove_roles(role)

      msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn chơi tất cả mọi game**")

    else:
      await interaction.author.remove_roles(kvc_role)

      game = ""
      for key in interaction.values:
        role = discord.utils.get(interaction.guild.roles, id=game_roles[key])
        await interaction.author.add_roles(role) 
        game += key+","

      game = game.rstrip(game[-1])
      msg = await interaction.message.channel.send("**"+interaction.author.mention+" đã chọn chơi: "+game+"**") 

    await asyncio.sleep(10)
    await msg.delete()
