from bot import *
from core.conf.bot.event_handlers import *
from core.env import env

if env.BOT_ONLY:
    bot.run(env.BOT_TOKEN)
else:
    from core.conf.api.conf import app
    from core.conf.api.event_handler import *
    from core.conf.api.routes import api_router

    # include all api routers
    app.include_router(api_router)

    @app.get("/api")
    def main_router():
        return {"status": "alive"}
