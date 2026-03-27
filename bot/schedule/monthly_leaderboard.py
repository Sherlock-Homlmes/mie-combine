# default
import asyncio
import datetime

# lib
import discord
from discord.ext import commands, tasks

# local
from bot.study_time.statistic import generate_leaderboard_info
from core.conf.bot.conf import server_info
from models.transactions import CurrencyUnitEnum, Transactions
from utils.time_modules import Now


class MonthlyLeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Schedule - Monthly leaderboard module ready")
        self.leaderboard_monthly.start()
        self.auto_reset_role_monthly.start()

    @tasks.loop(hours=720)
    async def leaderboard_monthly(self):
        leaderboard_info = await generate_leaderboard_info("Tháng trước")
        from_discord_user_id = 883974628136087562  # Mie bot
        transactions_to_insert = []
        time_module = Now()
        transactions_time = time_module.now
        last_month = time_module.first_day_of_next_month()

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
                    message=f"Betterme trao thưởng tháng {last_month.month}/{last_month.year}",
                    currency_unit=CurrencyUnitEnum.VND,
                    created_at=transactions_time,
                )
            )

        with open(leaderboard_info.img_path, "rb") as f:

            def mention(member_id) -> str:
                return f"<@{member_id}>"

            user_mention_content = f"Top 1: {mention(leaderboard_info.member_ids[0])}\n"
            user_mention_content += (
                f"Top 2: {mention(leaderboard_info.member_ids[1])}\n"
            )
            user_mention_content += (
                f"Top 3: {mention(leaderboard_info.member_ids[2])}\n"
            )
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
    async def auto_reset_role_monthly(self):
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
                try:
                    await member.remove_roles(role)
                except Exception as e:
                    print(
                        f"Error removing role {role.name} from member {member.display_name}: {e}"
                    )

    @leaderboard_monthly.before_loop
    async def before_leaderboard_monthly(self):
        await self.bot.wait_until_ready()
        time_module = Now()
        now = time_module.now
        first_day_of_next_month = (
            time_module.first_day_of_next_month() + datetime.timedelta(minutes=30)
        )
        delta = (first_day_of_next_month - now).total_seconds()
        await asyncio.sleep(delta)

    @auto_reset_role_monthly.before_loop
    async def before_auto_reset_role_monthly(self):
        time_module = Now()
        now = time_module.now
        first_day_of_next_month = time_module.first_day_of_next_month()
        time_module.first_day_of_next_month() + datetime.timedelta(minutes=30)
        delta = (first_day_of_next_month - now).total_seconds()
        await asyncio.sleep(delta)


async def setup(bot):
    await bot.add_cog(MonthlyLeaderboardCog(bot))
