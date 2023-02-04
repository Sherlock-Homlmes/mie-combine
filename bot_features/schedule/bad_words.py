# default
import asyncio

# lib
from discord.ext import tasks

# local
from base import bot
from models import BadUsers
from feature_func.time_modules import vn_now


@tasks.loop(hours=1)
async def unmute_badword():
    await bot.wait_until_ready()
    await asyncio.sleep(30)

    delete_bad_users = await BadUsers.find().to_list()

    for bad_user in delete_bad_users:
        if (vn_now() - bad_user.created_at).days >= 30:
            await bad_user.delete()
