from bot import bot

from .confession import *


@bot.listen()
async def on_ready():
    print("5.Confession ready")
