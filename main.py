# Run bot only
from core.env import env
from core.bot_conf.conf import bot
from core.bot_conf.event_handlers import *

bot.run(env.BOT_TOKEN)
