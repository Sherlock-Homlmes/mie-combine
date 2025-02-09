# default
import asyncio

# local
from core.conf.bot.conf import bot

from .auto_restart_bot import restart_bot
from .auto_scan_user_name import scan_user_name
from .static_channels import static_channels


@bot.listen()
async def on_ready():
    print("1. Schedule included")
    await asyncio.sleep(20)
    restart_bot.start()
    scan_user_name.start()
    static_channels.start()
    print("1. Schedule ready")
