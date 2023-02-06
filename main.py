from all_env import my_secret, bot_only

if bot_only:
    from bot import bot

    bot.run(my_secret)
else:
    import uvicorn
    from api import app

    uvicorn.run(app, host="0.0.0.0", port=8080)
