# lib
import discord
from beanie.odm.operators.update.general import Set
from discord.ext import commands

# local
from models import Users
from utils.time_modules import Now


class OnMemberLeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Guild event - On member leave module ready")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot._fully_ready.wait()

        if not member.avatar:
            avatar = member.default_avatar.url
        else:
            avatar = member.avatar.url
        await Users.find_one(Users.discord_id == member.id).upsert(
            Set(
                {
                    Users.name: member.name,
                    Users.nick: member.nick,
                    Users.avatar: avatar,
                    Users.is_bot: member.bot,
                    Users.is_in_server: False,
                    Users.leaved_at: Now().now,
                }
            ),
            on_insert=Users(
                discord_id=member.id,
                name=member.name,
                nick=member.nick,
                avatar=avatar,
                is_bot=member.bot,
                is_in_server=False,
                created_at=member.created_at,
                joined_at=member.joined_at,
            ),
        )
        print(f"{member} have leaved server")


async def setup(bot):
    await bot.add_cog(OnMemberLeaveCog(bot))
