from all_env import *
from base import bot, discord

try:
    bot.run(my_secret)
except discord.errors.HTTPException:
    if environment == "replit":
        os.system("kill 1")
