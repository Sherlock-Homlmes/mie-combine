from bot import bot
from .study_time import *


@bot.listen()
async def on_ready():
    print("7.Study time ready")
