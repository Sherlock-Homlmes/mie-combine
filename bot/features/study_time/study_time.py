# lib
import discord
from pydantic.error_wrappers import ValidationError
import asyncio

# local
from bot import bot
from discord import app_commands
from bot.features.guild_event.on_member_join import on_member_join
from models import Users, UserStudySection, UserDailyStudyTime
from other_modules.time_modules import Now

updating_members = []


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    if not member_before.channel and member_after.channel:
        while member.id in updating_members:
            await asyncio.sleep(1)
        updating_members.append(member.id)
        print(member.name, member.id, "in")
        try:
            user_study_section = await UserStudySection.find_one(
                UserStudySection.user.discord_id == str(member.id),
                fetch_links=True,
            )
            if user_study_section:
                user_study_section.start_study_time = Now().now
                await user_study_section.save()
            else:
                await UserStudySection(
                    user=await Users.find_one(Users.discord_id == str(member.id)),
                    start_study_time=Now().now,
                ).insert()

        # if user not in users database
        except ValidationError as e:
            print(e)
            await on_member_join(member=member)
            await UserStudySection(
                user=await Users.find_one(Users.discord_id == str(member.id)),
                start_study_time=Now().now,
            ).insert()

    elif member_before.channel and not member_after.channel:
        print(member.name, member.id, "out")
        user_study_section = await UserStudySection.find_one(
            UserStudySection.user.discord_id == str(member.id), fetch_links=True
        )
        try:
            await user_study_section.delete()
        except AttributeError as e:
            print(e)
        if member.id in updating_members:
            updating_members.remove(member.id)
            print("not in updating member anymore")


@bot.tree.command(name="study_time", description="Xem tổng thời gian học")
@app_commands.describe(member="Member")
@app_commands.default_permissions(administrator=True)
async def end(interaction: discord.Interaction, member: discord.Member):
    total_time = await UserDailyStudyTime.get_user_total_study_time(user_id=member.id)
    if total_time:
        content = f"Tổng thời gian học: {total_time}"
    else:
        content = "Bạn chưa học trong BetterMe"
    await interaction.response.send_message(content)
