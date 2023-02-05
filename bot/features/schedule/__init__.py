# default
import asyncio

# local
from bot import bot

from .static_channels import static_channels


@bot.listen()
async def on_ready():
    print("1.Schedule ready")
    await asyncio.sleep(10)
    static_channels.start()
