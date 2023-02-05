# lib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# local
from bot import bot
from all_env import my_secret

app = FastAPI(docs_url="/all-api", redoc_url=None)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

is_bot_start = False


@app.get("/")
async def home():
    global is_bot_start

    if not is_bot_start:
        is_bot_start = True
        await bot.start(my_secret)

    return "Hello I'm alive"
