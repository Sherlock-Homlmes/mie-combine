from re import M
from base import (
    # necess
    bot,
    tasks,
    get,
    # var
    guild_id,
    homie_id,
    easter_eggs_id)

from feature_func.mongodb.homie import homie_data, update_data

homie_list = []

@bot.listen()
async def on_ready():
    global homie_list, guild

    guild = bot.get_guild(guild_id)
    homie_role = get(guild.roles, id=homie_id)
    for homie in homie_role.members:
        if homie.id not in homie_list:
            homie_list.append(homie.id)


async def update_homie(data: list):
    global guild
    print(homie_data)

    for d in data:
        member_id = d[0]
        if member_id not in homie_list:
            member_id = str(member_id)
            if member_id not in homie_data.keys():
                homie_data[member_id] = 0
            else:
                homie_data[member_id] += 1

            if homie_data[member_id] >= 5000:
                easter_eggs_role = get(guild.roles, id=easter_eggs_id)
                homie_role = get(guild.roles, id=homie_id)

                user = guild.get_member(int(member_id))
                await user.add_roles(easter_eggs_role)
                await user.add_roles(homie_role)
                homie_list.append(int(member_id))
                del homie_data[member_id]

                try:
                    await user.send(user.mention +"**Chúc mừng bạn đã có Easter Egg: Homie**")
                except Exception as e:
                    print(e)

    print(homie_data)
    update_data(homie_data)

