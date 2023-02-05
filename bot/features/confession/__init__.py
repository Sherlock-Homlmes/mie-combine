from .confession import *


from bot import bot


@bot.listen()
async def on_ready():
    print("5.Confession ready")
