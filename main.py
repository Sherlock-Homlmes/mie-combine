# lib
import uvicorn

# local
from api import *
from all_env import my_secret


def run_api_and_bot():
    uvicorn.run(app, host="0.0.0.0", port=8080)


def run_bot_only():
    bot.run(my_secret)


run_bot_only()
