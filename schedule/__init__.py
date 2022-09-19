from .static_channels import static_channels

from base import bot
@bot.listen()
async def on_ready():
	static_channels.start()
	print('1.Schedule ready')