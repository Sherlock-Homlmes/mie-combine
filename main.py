import os
from all_env import *

# try:
#   from base import bot
#   from keep_alive import keep_alive
# except  Exception as e:
#   print(f"Error: {e}")
#   os.system("pip install discord")
#   os.system("pip install git+https://github.com/kiki7000/discord.py-components")
#   os.system("pip install pytz")
#   os.system("pip install uvicorn")
#   os.system("pip install fastapi")
  
from base import bot
from keep_alive import keep_alive

if environment == "local":
  bot.run(my_secret)
elif environment == "replit":
  keep_alive()
  try:
    bot.run(my_secret)
  except Exception as e:
    os.system("kill 1")
    bot.run(my_secret)