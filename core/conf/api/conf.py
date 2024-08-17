# default
# libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

# basic config
app = FastAPI(
    title="MIE BOT API",
    version="0.1.0",
    # disable docs in user portal
    docs_url="/api/docs",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
)

allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# app.mount("/api/media", StaticFiles(directory="scrap/data/media"), name="media")
