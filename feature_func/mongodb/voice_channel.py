from all_env import dtbs

dtb = dtbs["create_voice_channel"]

example_data = {
    "owner_id": int,
    "vc_id":  int,
    "cc_id": int
}

# before create
def get_all_vc():
    all_vc = dtb.find()
    all_vc_id = []
    for vc in all_vc:
        all_vc_id.append(vc["vc_id"])
    
    return all_vc_id

# function
def find_vc(vc_id: int):
    return dtb.find_one({"vc_id":vc_id})

def create_vc(owner_id: int, vc_id: int, cc_id: int):
    data = {
        "owner_id": owner_id,
        "vc_id":  vc_id,
        "cc_id": cc_id
    }
    dtb.insert_one(data)

def delete_vc(vc_id: int):
    dtb.delete_one({"vc_id":vc_id})
