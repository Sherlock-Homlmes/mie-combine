# lib
import asyncio

import discord
from discord import app_commands

# local
from bot import bot
from bot.features.guild_event.on_member_join import on_member_join
from models import UserDailyStudyTime, Users, UserStudySection
from other_modules.time_modules import Now

updating_members = []


@bot.listen()
async def on_ready():
    print("7.Study time ready")


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    # member join channel
    if not member_before.channel and member_after.channel:
        # block transaction async
        while member.id in updating_members:
            await asyncio.sleep(1)
        updating_members.append(member.id)
        # if user in users database
        try:
            # add study section
            user_study_section = await UserStudySection.find_one(
                UserStudySection.user.discord_id == str(member.id),
                fetch_links=True,
            )
            # check if exist study section
            if user_study_section:
                user_study_section.start_study_time = Now().now
                await user_study_section.save()
            # if not exist study section
            else:
                await UserStudySection(
                    user=await Users.find_one(Users.discord_id == str(member.id)),
                    start_study_time=Now().now,
                ).insert()

        # if user not in users database
        except Exception:
            await on_member_join(member=member)
            await UserStudySection(
                user=await Users.find_one(Users.discord_id == str(member.id)),
                start_study_time=Now().now,
            ).insert()

    # member leave channel
    elif member_before.channel and not member_after.channel:
        user_study_section = await UserStudySection.find_one(UserStudySection.user.discord_id == str(member.id), fetch_links=True)
        try:
            await user_study_section.delete()
        except AttributeError as e:
            print("Study time Error:", e)
        if member.id in updating_members:
            updating_members.remove(member.id)


@bot.tree.command(name="member_study_time")
@app_commands.describe(member="Member")
@app_commands.default_permissions(administrator=True)
async def member_study_time(interaction: discord.Interaction, member: discord.Member):
    total_time = await UserDailyStudyTime.get_user_total_study_time(user_id=member.id)
    if total_time:
        content = f"Tổng thời gian học: {total_time}"
    else:
        content = "Bạn chưa học trong BetterMe"
    await interaction.response.send_message(content)


@bot.tree.command(name="study_time", description="Xem tổng thời gian học")
async def study_time(interaction: discord.Interaction):
    total_time = await UserDailyStudyTime.get_user_total_study_time(user_id=interaction.user.id)
    if total_time:
        content = f"Tổng thời gian học: {total_time}'"
    else:
        content = "Bạn chưa học trong BetterMe"
    await interaction.response.send_message(content)


@bot.tree.command(name="daily", description="Xem thời gian học hôm nay")
async def daily(interaction: discord.Interaction):
    total_time = await UserDailyStudyTime.find_one(
        UserDailyStudyTime.user.discord_id == str(interaction.user.id),
        UserDailyStudyTime.date == Now().today,
        fetch_links=True,
    )
    if total_time:
        content = f"Thời gian học hôm nay: {total_time.study_time}"
    else:
        total_time = [0] * 24
        content = "Bạn chưa học hôm nay"

    await interaction.response.send_message(content)
