from core.conf.bot.event_handlers import *
from core.env import env

if env.BOT_ONLY:
    print("Running bot only")
    bot.run(env.BOT_TOKEN)  # noqa: F405
else:
    from core.conf.api.conf import app
    from core.conf.api.event_handler import *
    from core.conf.api.routes import app_router

    print("Running bot and api")

    # include all api routers
    app.include_router(app_router)

    @app.get("/api")
    def main_router():
        return {"status": "alive"}
