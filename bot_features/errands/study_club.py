import os
import asyncio

from base import (
    # necess
    discord,
    bot,
    tasks,
    get, has_permissions, Interaction,
    # var
    admin_id,
)
from feature_func.stable_json import open_database, write_database, fix_database

database_directory = "/general/general"
fix_database(database_directory)

study_club_interaction_id = open_database(
    database_directory)["study_club_interaction_id"]
study_clubs = open_database("/study_club/study_club")

change = False


@bot.listen()
async def on_interaction(interaction: Interaction):
    global change, study_clubs, study_club_interaction_id

    if change:
        change = False
        study_club_interaction_id = open_database(
            database_directory)["study_club_interaction_id"]
        study_clubs = open_database("/study_club/study_club")

    if interaction.message:
        if interaction.message.id == study_club_interaction_id and interaction.type == discord.InteractionType.component:
            values = interaction.data["values"]

            if "none" in values:
                for key, value in study_clubs.items():
                    if key != "none":
                        category = bot.get_channel(value["category_id"])
                        writing_channel = bot.get_channel(value["writing_channel"])
                        await category.set_permissions(interaction.user,
                                                    overwrite=None)
                        await writing_channel.set_permissions(interaction.user,
                                                            overwrite=None)
                        await interaction.user.send(
                            f"Bạn đã rời tất cả các Languages Club")
            else:
                for interact in values:
                    category = bot.get_channel(
                        study_clubs[interact]["category_id"])
                    writing_channel = bot.get_channel(
                        study_clubs[interact]["writing_channel"])
                    await category.set_permissions(interaction.user,
                                                read_messages=True)
                    await writing_channel.set_permissions(interaction.user,
                                                        read_messages=True,
                                                        send_messages=False)

                    club = study_clubs[interact]["title"]
                    await interaction.response.defer()
                    await interaction.user.send(f"Chào mừng bạn đến với { club }")


# @bot.command(name="study_club")
# @has_permissions(administrator= True)
# async def _study_club(ctx):
#     global study_clubs, change

#     if ctx.user.id in admin_id:

#         options = []
#         for key, value in study_clubs.items():
#             options.append(
#                 SelectOption(
#                     label=value["title"],
#                     value=key,
#                     #emoji=question
#                 ), )

#         msg = await ctx.send(
#             "**Languages Club**",
#             components=[
#                 Select(
#                     placeholder="Languages Club",
#                     # max_values = len(study_clubs.keys()),
#                     options=options)
#             ])

#         change = True
#         data = open_database(database_directory)
#         data["study_club_interaction_id"] = msg.id
#         write_database(data, database_directory)
