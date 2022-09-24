from all_env import dtbs

import datetime
import pytz

dtb = dtbs["ai_chatbot_data"]
number_docs = dtb.count_documents({})

def create_data(value: list):
    global number_docs

    # number
    number_docs += 1
    # time stamp
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))

    # insert data
    data = {}
    data["id"] = number_docs + 1
    data["time"] = pst_now
    data["value"] = value
    dtb.insert_one(data)