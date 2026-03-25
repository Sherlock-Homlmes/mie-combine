# default
import asyncio

# lib
import discord

from bot.guild_event.on_member_join import on_member_join

# local
from core.conf.bot.conf import bot, server_info
from models import UserDailyStudyTimes, Users, UserStudySection
from utils.time_modules import Now

updating_members = []


@bot.listen()
async def on_voice_state_update(
    member: discord.Member,
    member_before: discord.VoiceState,
    member_after: discord.VoiceState,
):
    # if member.bot or member.id != 880359404036317215:
    if member.bot:
        return

    await bot._fully_ready.wait()

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
                UserStudySection.user.discord_id == member.id,
                fetch_links=True,
            )
            # check if exist study section
            if user_study_section:
                user_study_section.start_study_time = Now().now
                await user_study_section.save()
            # if not exist study section
            else:
                await UserStudySection(
                    user=await Users.find_one(Users.discord_id == member.id),
                    start_study_time=Now().now,
                ).insert()

        # if user not in users database
        except Exception:
            await on_member_join(member=member)
            await UserStudySection(
                user=await Users.find_one(Users.discord_id == member.id),
                start_study_time=Now().now,
            ).insert()

    # member leave channel
    elif member_before.channel and not member_after.channel:
        user_study_section = await UserStudySection.find_one(
            UserStudySection.user.discord_id == member.id, fetch_links=True
        )
        try:
            await user_study_section.delete()
        except AttributeError as e:
            print("Study time Error:", e)
        if member.id in updating_members:
            updating_members.remove(member.id)

        # TODO: cache this
        member_db = await Users.find_one({"discord_id": member.id})
        if member_db.metadata and member_db.metadata.disable_achievement_role:
            return

        # Add positive student role and update monthly role
        await update_user_positive_student_role(member)
        await update_user_monthly_role(member)


async def update_user_positive_student_role(
    member: discord.Member, should_send_message: bool = True
):
    """Grant positive_student role if user qualifies (200h+ total study time)"""
    member_role_ids = [role.id for role in member.roles]
    if server_info.role_ids.positive_student not in member_role_ids:
        user_study_stats = await UserDailyStudyTimes.get_user_study_time_stats(
            member.id
        )
        if user_study_stats.total >= 200 * 60:
            await member.add_roles(server_info.roles.positive_student)
            if should_send_message:
                embed = discord.Embed(
                    title="**Chúc mừng**",
                    description="Bạn đã học hơn 200h và đạt được danh hiệu học sinh tích cực. Giờ đây bạn có thể đổi màu tên của bạn bất kì lúc nào bạn muốn bằng lệnh `/color`",
                    colour=discord.Colour.gold(),
                )
                try:
                    await member.send(embed=embed)
                except Exception:
                    print(
                        "Study time ranking error: Can not send message positive student to user"
                    )


async def update_user_monthly_role(
    member: discord.Member,
):
    member_role_ids = [role.id for role in member.roles]
    time_module = Now()
    user_study_stats = await UserDailyStudyTimes.get_user_study_time_stats(
        member.id, time_module.first_day_of_month(), time_module.last_day_of_month()
    )
    if user_study_stats.total >= 60:
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
        all_roles = [
            monthly_role_study_time["role"]
            for monthly_role_study_time in monthly_role_study_times
        ]
        for monthly_role_study_time in monthly_role_study_times:
            if monthly_role_study_time["role_id"] in member_role_ids:
                break
            if user_study_stats.total >= monthly_role_study_time["time"]:
                embed = discord.Embed(
                    title="**Chúc mừng**",
                    description=f"Bạn đã đạt được hạng **{monthly_role_study_time['name']}** trong tháng này.",
                    colour=discord.Colour.gold(),
                )
                icon_rank_img = discord.File(
                    f"./assets/rank_icon/{monthly_role_study_time['name'].lower()}.png",
                    filename=f"{monthly_role_study_time['name'].lower()}.png",
                )
                embed.set_thumbnail(
                    url=f"attachment://{monthly_role_study_time['name'].lower()}.png"
                )
                for role in all_roles:
                    if role.id in member_role_ids:
                        await member.remove_roles(role)
                await member.add_roles(monthly_role_study_time["role"])
                try:
                    await member.send(file=icon_rank_img, embed=embed)
                except Exception:
                    print("Study time ranking error: Can not send message to user")
                break
