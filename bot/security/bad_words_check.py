# default
from datetime import timedelta

#  lib
import discord
from discord import ui

# local
from core.conf.bot.conf import bot, server_info
from core.models import BadUsers, BanFormEnum, Users
from utils.time_modules import Now

# level 1
# check if word is exact as bad word
exact_bad_words = [
    # vn
    "lồn",
    "conmemay",
    "đĩ",
    "đụ",
    "cock",
    "vl",
    "cl",
    "dm",
    "lìn",
    "cmn",
    "cmm",
    # eng
    "fuk",
    "cuming",
]


# level 2
# check if word include
included_bad_words = [
    # vn
    "dkm",
    "cai l",
    "chem chép",
    "chem chep",
    "vai l",
    "cặc",
    "cặk",
    "cẹc",
    "địt",
    "loz",
    "đjt",
    "buồi",
    "buoi`",
    "buoi'",
    "dái",
    "dai'",
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
    "djt",
    "vai lon",
    "thang lon",
    "thằng lon",
    "cai' lon",
    "cái lon",
    "con cac",
    "con lon",
    "dau lon",
    "đầu lon",
    "đầu cac",
    "đầu buoi",
    "biết lon",
    "biết buoi",
    "biết cac",
    "biết cak",
    "dau cac",
    "sục cu",
    "sục ku",
    "cục su",
    "kục su",
    "hãm lon",
    "hỗn làm",
    "ham~ lon",
    "ham lon",
    "hãm cac",
    "ham~ cac",
    "ham cac",
    "hãm cak",
    "ham~ cak",
    "ham cak",
    # en
    "wtf",
    "nigg",
    "niger",
]

# level 3
# exclude any seperate and check include
space_bad_words = [
    # vn
    "dkm",
    "cặk",
    "địt",
    "đjt",
    "buồi",
    "buoi`",
    "buoi'",
    "đéo",
    "đ!t",
    "d!t",
    "vklm",
    "dcmm",
    "đcmm",
    "vclm",
    "pussy",
    # en
    "blowjob",
    "titjob",
    "fuck",
    "fvck",
    "bitch",
]

seperate = [
    "-",
    " ",
    "_",
]


class RemoveFalseBadWordButton(ui.View):
    @ui.button(label="Remove", custom_id="remove-bad-word")
    async def select_callback(self, interaction, button):
        await interaction.response.defer()
        # TODO: fix this. currently not working with find_one
        model = await BadUsers.find(
            BadUsers.diary_message_id == interaction.message.id, fetch_links=True
        ).to_list()
        if not model:
            return
        model = model[0]
        embed = discord.Embed(colour=discord.Colour.green())
        embed.add_field(name="User", value=f"<@{model.user.discord_id}>", inline=True)
        embed.add_field(name="Moderator", value=interaction.message.author.mention, inline=True)
        embed.add_field(name="Content", value=model.bad_content, inline=True)
        await server_info.admin_false_bad_word_log_channel.send(embed=embed)
        await model.delete()
        member = await server_info.guild.fetch_member(model.user.discord_id)
        await member.edit(timed_out_until=None)


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


async def punish(mem_id: int, message_content: str, mem_name: str):
    mem_id = str(mem_id)
    await remove_exprired_bad_user(mem_id)

    model = await BadUsers(
        user=await Users.find_one(Users.discord_id == mem_id),
        bad_content=message_content,
        created_at=Now().now,
    ).insert()

    # number of mistake in recent 1 month
    counter = len(
        await BadUsers.find(BadUsers.user.discord_id == mem_id, fetch_links=True).to_list()
    )

    # counter <= 4: warn
    # counter <= 11: mute
    # counter > 11: ban
    print(mem_name, counter)
    if counter <= 4:
        form = BanFormEnum.WARN.value
        hours = 0
        penalize = "Cảnh báo"
        colour = discord.Colour.orange()
    else:
        colour = discord.Colour.red()
        if counter <= 11:
            mute_hour_count_map = {
                5: 3,
                6: 6,
                7: 12,
                8: 24,
                9: 72,
                10: 180,
                11: 360,
            }
            form = BanFormEnum.MUTE.value
            hours = mute_hour_count_map[counter]
            penalize = f"Thời gian chờ {hours} tiếng"

        elif counter > 11:
            form = BanFormEnum.BAN.value
            hours = 0
            penalize = "BAN !!!"

    return (form, hours, penalize, colour, model)


@bot.listen()
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if check_bad_words(message.content):
        return

    try:
        await message.delete()
    except discord.errors.NotFound:
        print("Bad word error: Not found message")

    # process mute time
    form, hours, penalize, colour, model = await punish(
        message.author.id, message.content, message.author.name
    )
    reason = "Ngôn từ không phù hợp"
    if form == BanFormEnum.BAN.value:
        await message.author.ban(reason=reason)
    elif form == BanFormEnum.MUTE.value:
        unmuted_time = discord.utils.utcnow() + timedelta(hours=hours)
        await message.author.timeout(unmuted_time, reason=reason)
    elif form == BanFormEnum.WARN.value:
        pass

    # send to channel
    embed = discord.Embed(title=None, description=f"**Lý do:** {reason}", colour=colour)
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

    diary_message = await server_info.diary_channel.send(
        embed=embed, view=RemoveFalseBadWordButton()
    )
    model.diary_message_id = diary_message.id
    await model.save()
