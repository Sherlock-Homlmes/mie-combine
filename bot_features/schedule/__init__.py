# default
import asyncio

# local
from base import bot

from .static_channels import static_channels


@bot.listen()
async def on_ready():
    await asyncio.sleep(20)
    static_channels.start()
    print("1.Schedule ready")
