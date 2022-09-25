import imp
from base import (
  # necess
  bot, tasks, get, discord
  # var

)

from feature_func.mongodb import open_database, write_database

@tasks.loop(hours= 1)
async def unmute_badword():
    await bot.wait_until_ready()

    bad_user = open_database("bad_words")

    free_people = []
    for user_id, value in bad_user.items():
        for bad_word in value['bad_word_list']:
            time_stamp = bad_word[0]
            now = discord.utils.utcnow().replace(tzinfo=None)
            
            delta_time = now - time_stamp
            print(delta_time)
            print(delta_time.days)
            if delta_time.days >= 30:
                bad_user[user_id]['bad_word_list'].remove(bad_word)
        if len(bad_user[user_id]['bad_word_list']) == 0:
            free_people.append(user_id)
    
    for user_id in free_people:
        del bad_user[user_id]

    write_database(bad_user, "bad_words")  
        
