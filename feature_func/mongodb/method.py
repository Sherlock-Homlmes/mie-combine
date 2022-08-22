from all_env import dtbs

dtb = dtbs["create_vc"]

def open_database(data_key):
	return dtb.find_one({"name":data_key})["value"]

def write_database(data,data_key):
	dtb.update_one({"name":data_key}, {'$set': {'value':data}})