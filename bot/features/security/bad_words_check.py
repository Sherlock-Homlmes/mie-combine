# default
from datetime import timedelta

#  lib
import discord

# local
from bot import bot, server_info
from models import Users, BadUsers
from other_modules.time_modules import Now

exact_bad_words = [
    "lồn",
    "conmemay",
    "đĩ",
    "đụ",
    "cuming",
    "cock",
    "đù",
    "vl",
    "lìn",
    "cmn",
]

included_bad_words = [
    "dkm",
    "cặc",
    "cặk",
    "cẹc",
    "bitch",
    "địt",
    "loz",
    "đjt",
    "djt",
    "buồi",
    "buoi`",
    "buoi'",
    "đm",
    "vcl",
    "đéo",
    "đ!t",
    "d!t",
    "clm",
    "cđm",
    "vkl",
    "vklm",
    "vcc",
    "vcđ",
    "vcd",
    "đcm",
    "dcm",
    "wtf",
    "fuk",
]

space_bad_words = [
    "dkm",
    "cặk",
    "bitch",
    "địt",
    "đjt",
    "djt",
    "buồi",
    "buoi`",
    "buoi'",
    "đéo",
    "đ!t",
    "d!t",
    "vkl",
    "vklm",
    "dcmm",
    "đcmm",
    "vclm",
    "pussy",
    "blowjob",
    "titjob",
    "wtf",
    "fuck",
]

seperate = [
    "-",
    " ",
]


def check_bad_words(content: str) -> bool:

    content = content.lower()
    content_words = content.split(" ")
    tempo_content = []

    for word in content_words:

        # check exact
        if word in exact_bad_words:
            return False

        # check included
        if word.startswith("http") or word.startswith(":"):
            tempo_content.append(word)
            pass
        else:
            for bad_word in included_bad_words:
                if bad_word in word:
                    return False

    # check space bad word
    for tempo in tempo_content:
        content_words.remove(tempo)

    content = "".join(content_words)

    for seper in seperate:
        content = content.replace(seper, "")

    for word in space_bad_words:
        if word in content:
            return False

    return True


async def remove_exprired_bad_user(user_id: str):
    delete_bad_users = await BadUsers.find(
        BadUsers.user.discord_id == user_id, fetch_links=True
    ).to_list()

    for bad_user in delete_bad_users:
        if (Now().now - bad_user.created_at).days >= 30:
            await bad_user.delete()


async def punish(mem_id: int, message_content: str):
    mem_id = str(mem_id)
    await remove_exprired_bad_user(mem_id)

    bad_user = BadUsers(
        user=await Users.find_one(Users.discord_id == mem_id),
        bad_content=message_content,
        created_at=Now().now,
    )
    await bad_user.insert()

    counter = len(
        await BadUsers.find(
            BadUsers.user.discord_id == mem_id, fetch_links=True
        ).to_list()
    )

    if counter < 3:
        form = "WARN"
        hours = 0
        penalize = "Cảnh báo"
        colour = discord.Colour.orange()
    else:
        colour = discord.Colour.red()
        if counter <= 8:
            if counter == 3:
                hours = 3
            elif counter == 4:
                hours = 12
            elif counter == 5:
                hours = 24
            elif counter == 6:
                hours = 72
            elif counter == 7:
                hours = 180
            elif counter == 8:
                hours = 360

            form = "MUTE"
            penalize = f"Thời gian chờ {hours} tiếng"

        elif counter >= 9:
            form = "BAN"
            hours = 0
            penalize = f"BAN !!!"

    return (form, hours, penalize, colour)


### Các mức phạt:
# 1-2 lần: warn
# 3 lần: tempmute 3h
# 4 lần: tempmute 12h
# 5 lần: tempmute 24h
# 6 lần: tempmute 72h
# 7 lần: tempmute 360h
# 8 lần: ban


@bot.listen()
async def on_message(message: discord.Message):

    if check_bad_words(message.content) == False:

        try:
            await message.delete()
        except discord.errors.NotFound:
            print("Not found message")

        # xu ly
        form, hours, penalize, colour = await punish(message.author.id, message.content)
        reason = "Ngôn từ không phù hợp"
        if form == "WARN":
            pass
        elif form == "MUTE":
            unmuted_time = discord.utils.utcnow() + timedelta(hours=hours)
            await message.author.timeout(unmuted_time, reason=reason)
        elif form == "BAN":
            await message.author.ban(reason=reason)

        # send to channel
        embed = discord.Embed(
            title=None, description=f"**Lý do:** {reason}", colour=colour
        )
        embed.set_author(
            name=f"[{form}] {message.author.name}#{message.author.discriminator}",
            icon_url=message.author.avatar.url,
        )
        await message.channel.send(content=message.author.mention, embed=embed)

        # send to diary
        embed = discord.Embed(colour=colour)
        embed.set_author(
            name=f"[{form}] {message.author.name}#{message.author.discriminator}",
            icon_url=message.author.avatar.url,
        )
        embed.add_field(name="User", value=message.author.mention, inline=True)
        embed.add_field(name="Moderator", value=bot.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Channel", value=f"<#{message.channel.id}>", inline=False)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.add_field(name="Penalize", value=penalize, inline=False)

        await server_info.diary_channel.send(embed=embed)
