import os
from all_env import *

# try:
#   from base import bot
#   from keep_alive import keep_alive
# except  Exception as e:
#   print(f"Error: {e}")
#   os.system("pip install discord")
#   os.system("pip install pytz")
#   os.system("pip install uvicorn")
#   os.system("pip install fastapi")
  
from base import bot
from keep_alive import keep_alive

if environment == "replit":
  keep_alive()
bot.run(my_secret)