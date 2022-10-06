import io, json
import time

def fix_database(db_name:str):
     try:
          with open(f'data/{db_name}.json', encoding='utf-8') as f1:
               db = json.load(f1)
          with io.open(f'data/{db_name}_prevent.json', 'w', encoding='utf-8') as f:
               json.dump(db, f, ensure_ascii=False, indent=4)
     except:
          with open(f'data/{db_name}_prevent.json', encoding='utf-8') as f2:     
               db  = json.load(f2)        
          with io.open(f'data/{db_name}.json', 'w', encoding='utf-8') as f:
               json.dump(db, f, ensure_ascii=False, indent=4)

def open_database(db_name:str):
     with open(f'data/{db_name}.json', encoding='utf-8') as f1:
          db = json.load(f1)
     return db

def write_database(db,db_name:str):
     with io.open(f'data/{db_name}.json', 'w', encoding='utf-8') as f1:
       json.dump(db, f1, ensure_ascii=False, indent=4)
     with io.open(f'data/{db_name}_prevent.json', 'w', encoding='utf-8') as f2:
       json.dump(db, f2, ensure_ascii=False, indent=4)
