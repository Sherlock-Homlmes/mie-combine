######database
#
from pymongo import MongoClient
from threading import Thread
from waiting import wait

from all_env import dtbs
dtb = dtbs["errand_data"]

#start
#########################################advance#####################################
data_key = "cre_vc"
#cre_data
def cre_data(name,value):
	default_data ={
	"name":name,
	"value":value
	}
	dtb.insert_one(default_data)

#take_data
def take_data(name):
    tests = dtb.find( { "name":name } )
    for test in tests:
        return test["value"]

db = take_data(data_key)
stable_db = take_data(data_key)    
########def
def open_again(name):
    global db,stable_db
    dtb.update_one({ "name": name },  {'$set': {'value':db}} )
    stable_db = take_data(data_key)
	
def run1():
  global db,stable_db
  while True:
    wait(lambda: db != stable_db, timeout_seconds=None)
    open_again(data_key)
    
t1 = Thread(target=run1)
t1.start()

