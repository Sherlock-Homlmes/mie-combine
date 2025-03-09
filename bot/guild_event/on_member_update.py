# lib
import discord
from beanie.odm.operators.update.general import Set

# local
from core.conf.bot.conf import bot
from core.models import Users


# TODO: refactor this. duplicate with on_member_join
@bot.listen()
async def on_member_update(_: discord.Member, member_after: discord.Member):
    if not member_after.avatar:
        avatar = member_after.default_avatar.url
    else:
        avatar = member_after.avatar.url
    await Users.find_one(Users.discord_id == str(member_after.id)).upsert(
        Set(
            {
                Users.name: member_after.name,
                Users.nick: member_after.nick,
                Users.is_bot: member_after.bot,
                Users.avatar: avatar,
                Users.joined_at: member_after.joined_at,
            }
        ),
        on_insert=Users(
            discord_id=str(member_after.id),
            name=member_after.name,
            nick=member_after.nick,
            avatar=avatar,
            is_bot=member_after.bot,
            created_at=member_after.created_at,
            joined_at=member_after.joined_at,
        ),
    )

    # import time
    # import asyncio
    # if member_after.bot or member_after.id != 880359404036317215:
    #     return
    # start_time = time.time()

    # update_queries = []
    # for member in server_info.guild.members:
    #     avatar = member.avatar.url if member.avatar else member.default_avatar.url
    #     update_queries.append(
    #         Users.find_one(Users.discord_id == str(member.id)).upsert(
    #         Set(
    #             {
    #                 Users.name: member.name,
    #                 Users.nick: member.nick,
    #                 Users.is_bot: member.bot,
    #                 Users.avatar: avatar,
    #                 Users.joined_at: member.joined_at,
    #             }
    #         ),
    #         on_insert=Users(
    #             discord_id=str(member.id),
    #             name=member.name,
    #             nick=member.nick,
    #             avatar=avatar,
    #             is_bot=member.bot,
    #             created_at=member.created_at,
    #             joined_at=member.joined_at,
    #         ),
    #     )
    #     )

    # print('start update')
    # await asyncio.gather(*update_queries)

    # print("--- %s seconds ---" % (time.time() - start_time))
    # return
