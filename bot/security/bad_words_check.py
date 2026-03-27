# default
import re
from datetime import timedelta
from typing import Set

#  lib
import discord
from discord import ui
from discord.ext import commands

# local
from core.conf.bot.conf import server_info
from models import BadUsers, BanFormEnum, Users
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
    "duma",
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
    # "atangtest",
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
    "ditme",
    "vcl",
    "đéo",
    "đ!t",
    "d!t",
    "clm",
    "cđm",
    "vailon",
    "vai lon",
    "vailin",
    "vkl",
    "vklm",
    "vcc",
    "vcđ",
    "vcd",
    "đcm",
    "dcm",
    "djt",
    "thanglon",
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
    "căc.",
    "dit.",
    "đit.",
    "dmm",
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

# level 4
# replace alternative characters
alternative_words = {
    "I": "l",
}


def check_bad_words(self, content: str) -> Set[str | None]:
    alternative_content = content
    for key, value in alternative_words.items():
        alternative_content = alternative_content.replace(key, value)
    should_use_alternative = alternative_content != content

    content = content.lower()
    content = re.sub(r"\s+", " ", content)
    content_words = content.split(" ")
    match_bad_word: str | None = None
    match_type: str | None = None
    tempo_content = []

    for word in content_words:
        # check exact
        if word in exact_bad_words:
            match_bad_word = word
            match_type = "Exact"
            return (match_bad_word, match_type)

        # check included
        if word.startswith("http") or word.startswith(":"):
            tempo_content.append(word)
            pass
        else:
            for bad_word in included_bad_words:
                if bad_word in word:
                    match_bad_word = bad_word
                    match_type = "Included"
                    return (match_bad_word, match_type)

    # check space bad word
    for tempo in tempo_content:
        content_words.remove(tempo)

    content = "".join(content_words)

    for seper in seperate:
        content = content.replace(seper, "")

    for bad_word in space_bad_words:
        if bad_word in content:
            match_bad_word = bad_word
            match_type = "Included(remove seperate)"
            return (match_bad_word, match_type)

    if should_use_alternative:
        return check_bad_words(alternative_content)
    return (None, None)


class ReportFalseBadWordButton(ui.View):
    @ui.button(
        label="Báo cáo sai",
        style=discord.ButtonStyle.red,
        custom_id="report-false-bad-word",
    )
    async def report_callback(
        self, interaction: discord.Interaction, button: ui.Button
    ):
        await interaction.response.defer()
        # Find the BadUsers record by user_message_id
        model = await BadUsers.find(
            BadUsers.user_message_id == interaction.message.id, fetch_links=True
        ).to_list()
        if not model:
            await interaction.followup.send(
                "Không tìm thấy dữ liệu báo cáo.", ephemeral=True
            )
            return
        model = model[0]

        # Send link to diary message in false_bad_word_report_channel
        diary_message = await server_info.bad_word_log_channel.fetch_message(
            model.diary_message_id
        )
        message_link = diary_message.jump_url
        await server_info.false_bad_word_report_channel.send(message_link)

        # Disable the button
        button.disabled = True
        button.label = "Đã báo cáo"
        await interaction.message.edit(view=self)
        await interaction.followup.send("Đã gửi báo cáo thành công!", ephemeral=True)


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
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Content", value=model.bad_content, inline=True)
        await server_info.admin_false_bad_word_log_channel.send(embed=embed)

        # Send message to user that they've been cleared
        try:
            user = await server_info.guild.fetch_member(model.user.discord_id)
            await user.send("Bạn đã được gỡ bỏ cảnh báo từ hệ thống bad word.")
        except Exception as e:
            print(f"Cannot send DM to user: {e}")

        await model.delete()
        member = await server_info.guild.fetch_member(model.user.discord_id)
        await member.edit(timed_out_until=None)

        # Disable the button
        button.disabled = True
        button.label = "Đã xóa"
        await interaction.message.edit(view=self)
        await interaction.followup.send("Đã xóa cảnh báo thành công!", ephemeral=True)


class BadWordsCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Bad words check module ready")

    async def remove_exprired_bad_user(self, user_id: int):
        delete_bad_users = await BadUsers.find(
            BadUsers.user.discord_id == user_id, fetch_links=True
        ).to_list()

        for bad_user in delete_bad_users:
            if (Now().now - bad_user.created_at).days >= 30:
                await bad_user.delete()

    async def punish(self, user_id: int, message_content: str, mem_name: str):
        await self.remove_exprired_bad_user(user_id)

        model = await BadUsers(
            user=await Users.find_one(Users.discord_id == user_id),
            bad_content=message_content,
            created_at=Now().now,
        ).insert()

        # number of mistake in recent 1 month
        counter = len(
            await BadUsers.find(
                BadUsers.user.discord_id == user_id, fetch_links=True
            ).to_list()
        )

        # counter <= 6: warn
        # counter <= 12: mute
        # counter > 12: ban
        if counter <= 6:
            form = BanFormEnum.WARN.value
            hours = 0
            penalize = "Cảnh báo"
            colour = discord.Colour.orange()
        else:
            colour = discord.Colour.red()
            if counter <= 11:
                mute_hour_count_map = {
                    7: 0.5,
                    8: 2,
                    9: 4,
                    10: 24,
                    11: 72,
                    12: 180,
                }
                form = BanFormEnum.MUTE.value
                hours = mute_hour_count_map[counter]
                penalize = f"Thời gian chờ {hours} tiếng"

            elif counter > 11:
                form = BanFormEnum.BAN.value
                hours = 0
                penalize = "BAN !!!"

        return (form, hours, penalize, colour, model)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot._fully_ready.wait()

        if message.author.bot:
            return
        match_bad_word, match_type = check_bad_words(message.content)
        if not match_bad_word:
            return

        try:
            await message.delete()
        except discord.errors.NotFound:
            print("Bad word error: Not found message")

        # process mute time
        form, hours, penalize, colour, model = await self.punish(
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
        warn_embed = discord.Embed(
            title=None, description=f"**Lý do:** {reason}", colour=colour
        )
        warn_embed.set_author(
            name=f"[{form}] {message.author.name}#{message.author.discriminator}",
            icon_url=message.author.avatar.url,
        )
        await message.channel.send(content=message.author.mention, embed=warn_embed)

        # send to diary
        log_embed = discord.Embed(colour=colour)
        log_embed.set_author(
            name=f"[{form}] {message.author.name}#{message.author.discriminator}",
            icon_url=message.author.avatar.url,
        )
        log_embed.add_field(name="User", value=message.author.mention, inline=True)
        log_embed.add_field(
            name="Channel", value=f"<#{message.channel.id}>", inline=True
        )
        log_embed.add_field(name="Penalize", value=penalize, inline=True)
        log_embed.add_field(name="Message", value=message.content, inline=False)
        log_embed.add_field(
            name="Bad word", value=f"{match_type}: {match_bad_word}", inline=False
        )

        diary_message = await server_info.bad_word_log_channel.send(
            embed=log_embed, view=RemoveFalseBadWordButton()
        )
        model.diary_message_id = diary_message.id
        await model.save()

        # send to user
        user_warn_embed = discord.Embed(
            title=None, description=f"**Lý do:** {reason}", colour=colour
        )
        user_warn_embed.add_field(
            name="Channel", value=f"<#{message.channel.id}>", inline=True
        )
        user_warn_embed.add_field(name="Message", value=message.content, inline=False)
        user_warn_embed.add_field(name="Bad word", value=match_bad_word, inline=False)
        user_warn_message = await message.author.send(
            content='Bấm nút "Báo cáo sai" nếu từ bạn bị warn không đúng',
            embed=user_warn_embed,
            view=ReportFalseBadWordButton(),
        )
        model.user_message_id = user_warn_message.id
        await model.save()


async def setup(bot):
    await bot.add_cog(BadWordsCheckCog(bot))
