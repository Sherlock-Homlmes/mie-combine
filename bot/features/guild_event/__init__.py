from .on_member_join import *
from .on_member_leave import *


from bot import bot


@bot.listen()
async def on_ready():
    print("2.Guild event ready")
