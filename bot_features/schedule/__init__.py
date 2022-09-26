from .static_channels import static_channels
from .bad_words import unmute_badword

from base import bot
@bot.listen()
async def on_ready():
	unmute_badword.start()
	static_channels.start()
	print('1.Schedule ready')