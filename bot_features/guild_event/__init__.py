from .on_member_join import *
from .on_member_leave import *


from base import bot


@bot.listen()
async def on_ready():
    print("2.Guild event ready")
