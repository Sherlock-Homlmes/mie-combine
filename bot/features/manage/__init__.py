from bot import bot


@bot.listen()
async def on_ready():
    print("10.Manage staff ready")
