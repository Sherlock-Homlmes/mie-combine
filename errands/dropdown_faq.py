import asyncio

from base import (
    # necess
    discord,
    bot,
    tasks,
    get,Interaction,
    # var
    admin_id,
)
from feature_func.stable_json import open_database, write_database, fix_database

database_directory = "/general/general"
fix_database(database_directory)

change = False
faq_interaction_id = open_database(database_directory)["faq_interaction_id"]
faqs = open_database("/faq/faq")


@bot.listen()
async def on_interaction(interaction: Interaction):
    global change, faqs, faq_interaction_id

    if change:
        change = False
        faq_interaction_id = open_database(
            database_directory)["faq_interaction_id"]
        faqs = open_database("/faq/faq")

    if interaction.message.id == faq_interaction_id and interaction.type == discord.InteractionType.component:

        interact = interaction.data["values"][0]
        if interact in faqs and interact != "none":
            embed = discord.Embed(title=faqs[interact]["title"],
                                  description=faqs[interact]["description"],
                                  colour=discord.Colour.gold())

            for field in faqs[interact]["fields"]:
                embed.add_field(name=field[0], value=field[1], inline=False)

            embed.add_field(name="**Câu hỏi của**",
                            value=f"||{interaction.user.mention}||",
                            inline=False)
            embed.set_image(url="https://i.ibb.co/Wvw2CY9/Betterme.png")
            embed.set_footer(text='''BetterMe - Better everyday''')

            msg = await interaction.channel.send(embed=embed)
            await interaction.response.defer()
            await asyncio.sleep(60)
            await msg.delete()


# @bot.command(name="faq")
# async def faq(ctx):
#     global change, faqs, faq_interaction_id

#     if ctx.author.id in admin_id:

#         question = discord.utils.get(bot.emojis, name='ques_1')

#         embed = discord.Embed(title="**FAQ about BetterMe**",
#                               description='''
#       Nếu có gì các bạn không hiểu hãy chọn câu hỏi ở bên dưới Mie sẽ trả lời giúp bạn
# Nếu bạn vẫn không hiểu hay không có câu hỏi bạn muốn hãy nhắn vào kênh này chúng mình sẽ hỗ trợ bạn hết sức có thể
#       ''',
#                               colour=discord.Colour.gold())
#         embed.set_footer(text='''BetterMe - Better everyday''')

#         options = []
#         for ques, value in faqs.items():
#             options.append(
#                 SelectOption(label=value["title"], value=ques,
#                              emoji=question), )

#         msg = await ctx.send(
#             embed=embed,
#             components=[Select(placeholder="FAQ", options=options)])

#         change = True
#         data = open_database(database_directory)
#         data["faq_interaction_id"] = msg.id
#         write_database(data, database_directory)
