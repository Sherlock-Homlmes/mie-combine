# default
import asyncio
import datetime

# lib
import discord
from discord.ext import tasks

# local
from bot.study_time.statistic import generate_leaderboard_info
from core.conf.bot.conf import bot, server_info
from core.models.transactions import CurrencyUnitEnum, Transactions
from utils.time_modules import Now


@tasks.loop(hours=720)
async def leaderboard_monthly():
    leaderboard_info = await generate_leaderboard_info("Tháng trước")
    from_discord_user_id = 883974628136087562  # Mie bot
    transactions_to_insert = []
    transactions_time = Now().now

    for i, member_id in enumerate(leaderboard_info.member_ids):
        if i == 0:
            amount = 55555
        elif i == 1:
            amount = 33333
        elif i == 2:
            amount = 11111
        else:
            amount = 5555  # Top 4-10

        transactions_to_insert.append(
            Transactions(
                from_user_id=from_discord_user_id,
                to_user_id=member_id,
                amount=amount,
                currency_unit=CurrencyUnitEnum.VND,
                created_at=transactions_time,
            )
        )

    with open(leaderboard_info.img_path, "rb") as f:

        def mention(member_id) -> str:
            return f"<@{member_id}>"

        user_mention_content = f"Top 1: {mention(leaderboard_info.member_ids[0])}\n"
        user_mention_content += f"Top 2: {mention(leaderboard_info.member_ids[1])}\n"
        user_mention_content += f"Top 3: {mention(leaderboard_info.member_ids[2])}\n"
        top10_mention = "".join(
            [mention(member_id) for member_id in leaderboard_info.member_ids[3:]]
        )
        user_mention_content += f"Top 10: {top10_mention}"
        await asyncio.gather(
            *[
                Transactions.insert_many(transactions_to_insert),
                server_info.channels.leaderboard.send(
                    content=f"{leaderboard_info.content}\n{user_mention_content}",
                    file=discord.File(f),
                ),
            ]
        )


@tasks.loop(hours=720)
async def auto_reset_role_monthly():
    all_role_ids = [
        server_info.role_ids.challenger,
        server_info.role_ids.master,
        server_info.role_ids.diamond,
        server_info.role_ids.gold,
        server_info.role_ids.silver,
        server_info.role_ids.bronze,
        server_info.role_ids.iron,
    ]
    for role_id in all_role_ids:
        role = server_info.guild.get_role(role_id)
        for member in role.members:
            if member.id == 880359404036317215:
                await member.remove_roles(role)


@leaderboard_monthly.before_loop
async def before_leaderboard_monthly():
    await bot.wait_until_ready()
    time_module = Now()
    now = time_module.now
    first_day_of_next_month = time_module.first_day_of_next_month() + datetime.timedelta(hours=6)
    delta = (first_day_of_next_month - now).total_seconds()
    print("before_leaderboard_monthly: ", delta, " seconds")
    await asyncio.sleep(delta)


@auto_reset_role_monthly.before_loop
async def before_auto_reset_role_monthly():
    time_module = Now()
    now = time_module.now
    first_day_of_next_month = time_module.first_day_of_next_month()
    delta = (first_day_of_next_month - now).total_seconds()
    await asyncio.sleep(delta)
