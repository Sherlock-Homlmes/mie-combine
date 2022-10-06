from base import bot
from .create_vc import *

@bot.listen()
async def on_ready():
    print('6.API ready')