#
import json

#
import asyncio
import io, json

from waiting import wait
import time

#
import threading
from threading import Thread

db = None

def check_fail(db_name):
     try:
          with open(f'data/{db_name}.json', encoding='utf-8') as f1:
               db = json.load(f1)        
          with io.open(f'data/{db_name}_prevent.json', 'w', encoding='utf-8') as f2:
               json.dump(db, f2, ensure_ascii=False, indent=4)
     except:
          with open(f'data/{db_name}_prevent.json', encoding='utf-8') as f1:
               db = json.load(f1)  
          with io.open(f'data/{db_name}.json', 'w', encoding='utf-8') as f2:
               json.dump(db, f2, ensure_ascii=False, indent=4)

def open_database(db_name):
     global db, stable_db

     check_fail(db_name)

     with open(f'data/{db_name}.json', encoding='utf-8') as f1:
          db = json.load(f1)        
     with open(f'data/{db_name}_prevent.json', encoding='utf-8') as f2:
          stable_db = json.load(f2)            


def open_again(db_name):
     global db,stable_db

     with io.open(f'data/{db_name}.json', 'w', encoding='utf-8') as f1:
          json.dump(db, f1, ensure_ascii=False, indent=4)
     with io.open(f'data/{db_name}_prevent.json', 'w', encoding='utf-8') as f2:
          json.dump(db, f2, ensure_ascii=False, indent=4)

     with open(f'data/{db_name}.json', encoding='utf-8') as f:
          stable_db = json.load(f1)

def run(db_name):
     global db,stable_db
     while True:
          wait(lambda: db != stable_db, timeout_seconds=None)
          start_time = time.time()
          open_again(db_name)
          end_time = time.time()
          print('Total time elapsed: %.2f seconds' % (end_time - start_time))

def start_database(database_directory:str):
     open_database(database_directory)
     t1 = Thread(target=run(database_directory))
     t1.start()