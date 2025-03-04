# default
import asyncio

# lib
import discord

# local
from core.conf.bot.conf import bot
from bot.guild_event.on_member_join import on_member_join
from core.models import Users, UserStudySection
from utils.time_modules import Now


updating_members = []


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    if member.bot:
        return
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
        user_study_section = await UserStudySection.find_one(
            UserStudySection.user.discord_id == str(member.id), fetch_links=True
        )
        try:
            await user_study_section.delete()
        except AttributeError as e:
            print("Study time Error:", e)
        if member.id in updating_members:
            updating_members.remove(member.id)
