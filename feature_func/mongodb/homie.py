from all_env import dtbs

dtb = dtbs["errand_data"]
homie_data = dtb.find_one({"name": "homie"})["value"]

def update_data(value: dict):
    dtb.update_one({"name": "homie"}, {'$set': {'value': value}})

