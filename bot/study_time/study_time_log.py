# default
import asyncio

# lib
import discord

# local
from core.conf.bot.conf import bot, server_info
from bot.guild_event.on_member_join import on_member_join
from core.models import Users, UserStudySection, UserDailyStudyTimes
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
            # Add monthly rank role
            time_module = Now()
            user_study_stats = await UserDailyStudyTimes.get_user_study_time_stats(
                member.id, time_module.first_day_of_month(), time_module.last_day_of_month()
            )
            if user_study_stats.total < 60:
                return
            member_role_ids = [role.id for role in member.roles]
            monthly_role_study_times = [
                {
                    "time": 120 * 60,
                    "role": server_info.roles.challenger,
                    "role_id": server_info.role_ids.challenger,
                    "name": "Challenger",
                },
                {
                    "time": 90 * 60,
                    "role": server_info.roles.master,
                    "role_id": server_info.role_ids.master,
                    "name": "Master",
                },
                {
                    "time": 60 * 60,
                    "role": server_info.roles.diamond,
                    "role_id": server_info.role_ids.diamond,
                    "name": "Diamond",
                },
                {
                    "time": 30 * 60,
                    "role": server_info.roles.gold,
                    "role_id": server_info.role_ids.gold,
                    "name": "Gold",
                },
                {
                    "time": 10 * 60,
                    "role": server_info.roles.silver,
                    "role_id": server_info.role_ids.silver,
                    "name": "Silver",
                },
                {
                    "time": 3 * 60,
                    "role": server_info.roles.bronze,
                    "role_id": server_info.role_ids.bronze,
                    "name": "Bronze",
                },
                {
                    "time": 1 * 60,
                    "role": server_info.roles.iron,
                    "role_id": server_info.role_ids.iron,
                    "name": "Iron",
                },
            ]
            for monthly_role_study_time in monthly_role_study_times:
                if monthly_role_study_time["role_id"] in member_role_ids:
                    break
                if user_study_stats.total >= monthly_role_study_time["time"]:
                    await member.add_roles(monthly_role_study_time["role"])

                    embed = discord.Embed(
                        title="**Chúc mừng**",
                        description=f"bạn đã đạt được hạng **{monthly_role_study_time['name']}** trong tháng này.",
                        colour=discord.Colour.gold(),
                    )
                    icon_rank_img = discord.File(
                        f"./assets/rank_icon/{monthly_role_study_time['name'].lower()}.png",
                        filename=f"{monthly_role_study_time['name'].lower()}.png",
                    )
                    embed.set_thumbnail(
                        url=f"attachment://{monthly_role_study_time['name'].lower()}.png"
                    )
                    await member.send(file=icon_rank_img, embed=embed)
                    break

        except AttributeError as e:
            print("Study time Error:", e)
        if member.id in updating_members:
            updating_members.remove(member.id)
