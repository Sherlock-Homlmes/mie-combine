import signal
import asyncio

# libraries
import beanie

# local
from .conf import app
from core.env import env
from core.models import document_models
from core.database.mongodb import client
from core.conf.bot.conf import bot


running = True


# background task on startup
class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def run_discord_bot(self):
        print("Starting discord bot...")
        await bot.start(env.BOT_TOKEN)


runner = BackgroundRunner()


def stop_server(*args):
    global running
    running = False


async def connect_db() -> None:
    print("Connecting to database...")
    await beanie.init_beanie(
        database=client.discord_betterme,
        document_models=document_models,
    )
    print("Connect to database success")


@app.on_event("startup")
async def startup():
    global is_discord_bot_started, running

    # Set signal to detach when app stop
    signal.signal(signal.SIGTERM, stop_server)

    # CONNECT DB
    await connect_db()

    asyncio.create_task(runner.run_discord_bot())

    print("Start up done")


@app.on_event("shutdown")
async def shutdown_event():
    if bot.is_ready():
        await bot.close()
