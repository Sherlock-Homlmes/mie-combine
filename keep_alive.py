import uvicorn
from fastapi import FastAPI
from threading import Thread

app = FastAPI(docs_url="/all-api", redoc_url=None)


@app.get("/")
async def home():
    return "Hello. I'm alive"


def run_web():
    print("Run web")
    uvicorn.run(app, host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.start()
