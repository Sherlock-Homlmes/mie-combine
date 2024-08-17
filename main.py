from core.conf.api.conf import app
from core.conf.api.routes import api_router
from core.conf.api.event_handler import *
from core.conf.bot.event_handlers import *
from bot import *

# include all api routers
app.include_router(api_router)


@app.get("/api")
def main_router():
    return {"status": "alive"}
