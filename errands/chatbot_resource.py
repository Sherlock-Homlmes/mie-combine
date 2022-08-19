import os
from os import listdir
from os.path import isfile, join
database_directory = "./data/chat_bot_conver/"
resources_files = listdir(database_directory)
file = resources_files[0]
db_num = file.replace("resource_","")
db_num = db_num.replace("_prevent","")
db_num = db_num.replace(".json","")
db_num = int(db_num)

from base import (
  # necess
  bot,tasks,get,discord,
  #var
  bot_resource_channel_id
  )

from feature_func.stable_json import open_database,write_database,fix_database
database_directory = "chat_bot_conver/"
dbfile = database_directory + f"resource_{db_num}" 
fix_database(dbfile)

@bot.listen()
async def on_message(message):
  global dbfile,db_num

  if message.author.bot == False and message.content != "":
    try:
      db = open_database(dbfile)
    except:
      write_database([],dbfile)
      db = []
    db.append(message.content)
    write_database(db,dbfile)

    if len(db) >= 1000:
      
      channel = get(bot.get_all_channels(), id=bot_resource_channel_id)
      with open("data/"+dbfile+".json", 'rb') as f:
        await channel.send(file=discord.File(f))
        
      os.remove("data/"+dbfile+".json")
      os.remove("data/"+dbfile+"_prevent.json")
      
      db_num += 1
      dbfile = database_directory + f"resource_{db_num}"
      write_database([],dbfile)
