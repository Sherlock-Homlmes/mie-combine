from base import bot
from .app import app

import uvicorn
from threading import Thread


def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.start()

@bot.listen()
async def on_ready():
    keep_alive()
    print('8.API ready')
