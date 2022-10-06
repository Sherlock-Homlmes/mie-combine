from base import (
    # necess
    bot,
    tasks,
    get,
    discord,
    # var
    guild_id,
    admin_id,
    easter_eggs_id,
    lovesick_id)

from feature_func.stable_json import open_database, write_database, fix_database

general_database_directory = "/general/general"
fix_database(general_database_directory)

lovesick_list = []
lovesick_interaction_id = open_database(
    general_database_directory)["lovesick_interaction_id"]


@bot.listen()
async def on_ready():
    global lovesick_list, guild

    guild = bot.get_guild(guild_id)
    lovesick_role = get(guild.roles, id=lovesick_id)
    for lovesick in lovesick_role.members:
        if lovesick.id not in lovesick_list:
            lovesick_list.append(lovesick.id)


@bot.command(name="lovesick")
async def _lovesick(ctx):
    global lovesick_interaction_id

    if ctx.author.id in admin_id:

        guild = bot.get_guild(guild_id)
        emo_list = ["chuaherapxiec", "hug", "friend_zone", "nongcamcuakhui"]
        emojis = []
        for emo in emo_list:
            emojis.append(get(guild.emojis, name=emo))

        message = await ctx.send(
            file=discord.File("data/lovesick/lovesick.mp4"))

        data = open_database(general_database_directory)
        data["lovesick_interaction_id"] = lovesick_interaction_id = message.id
        write_database(data, general_database_directory)

        for emoji in emojis:
            await message.add_reaction(emoji)


@bot.listen()
async def on_raw_reaction_add(payload):
    global lovesick_interaction_id
    if payload.message_id == lovesick_interaction_id and len(
            lovesick_list) < 10 and payload.member.id not in lovesick_list:
        if payload.emoji == get(guild.emojis, name="friend_zone"):
            easter_eggs_role = get(guild.roles, id=easter_eggs_id)
            lovesick_role = get(guild.roles, id=lovesick_id)
            await payload.member.add_roles(easter_eggs_role)
            await payload.member.add_roles(lovesick_role)
            await payload.member.send(
                payload.member.mention +
                f"**Chúc mừng bạn là người thứ {len(lovesick_list)+1}/10 có Easter Egg: Đôi mắt kẻ si tình**"
            )
            lovesick_list.append(payload.member.id)

@bot.listen()
async def on_raw_reaction_remove(payload):
  global lovesick_interaction_id,guild
  if payload.message_id == lovesick_interaction_id and payload.emoji == get(guild.emojis, name="friend_zone"):
      lovesick_role = get(guild.roles, id=lovesick_id)
      member = guild.get_member(payload.user_id)
      await member.remove_roles(lovesick_role)
      if member.id in lovesick_list:
        lovesick_list.remove(member.id)