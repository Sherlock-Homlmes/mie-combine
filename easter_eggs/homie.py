from base import (
    # necess
    bot,
    tasks,
    get,
    # var
    guild_id,
    homie_id,
    easter_eggs_id)

from feature_func.stable_json import open_database, write_database, fix_database

mess_count_directory = "/homie/homie"
fix_database(mess_count_directory)

homie_list = []


@bot.listen()
async def on_ready():
    global homie_list, guild

    guild = bot.get_guild(guild_id)
    homie_role = get(guild.roles, id=homie_id)
    for homie in homie_role.members:
        if homie.id not in homie_list:
            homie_list.append(homie.id)


@bot.listen()
async def on_message(message):
    global homie_list

    if message.author.id not in homie_list and message.author.bot == False:
        db = open_database(mess_count_directory)

        if str(message.author.id) in db.keys():
            db[str(message.author.id)] += 1
            if db[str(message.author.id)] >= 5000:
                guild = bot.get_guild(guild_id)
                easter_eggs_role = get(guild.roles, id=easter_eggs_id)
                homie_role = get(guild.roles, id=homie_id)

                user = guild.get_member(message.author.id)
                await user.add_roles(easter_eggs_role)
                await user.add_roles(homie_role)
                await message.channel.send(
                    message.author.mention +
                    "**Chúc mừng bạn đã có Easter Egg: Homie**")

                homie_list.append(message.author.id)
                del db[str(message.author.id)]

        else:
            db[str(message.author.id)] = 1

        write_database(db, mess_count_directory)
