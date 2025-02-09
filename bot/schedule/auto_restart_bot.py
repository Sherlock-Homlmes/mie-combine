# default
import datetime
import os
import sys

# lib
from discord.ext import tasks


# Restart bot every 3:30 A.M Vietnamese
@tasks.loop(
    time=[
        datetime.time(hour=20, minute=30),
    ]
)
async def restart_bot():
    print("Restarting bot...")
    os.execv(sys.executable, ["python"] + sys.argv)
    restart_bot()
