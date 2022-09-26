from .homie import *
from .lovesick_eyes import *


from base import bot
@bot.listen()
async def on_ready():
	print('4.Easter egg ready')