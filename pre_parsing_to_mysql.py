import mysql.connector
import json


config = {'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'x-com',
  'raise_on_warnings': True}


db = mysql.connector.connect(**config)
cursor = db.cursor()

with open('./categories.json', 'r', encoding='utf-8') as file:
    categories_db = json.load(file)

# INSERT INTO category VALUES ('
#    id', 'category'
# );
category = ''
category_id = 1
subcategory_id = 1
category_insert = ("INSERT INTO category VALUES (%s, %s)")
subcategory_insert = ("INSERT INTO subcategory VALUES (%s, %s, %s)")


for category in categories_db.keys():
    category_data = (category_id, category)
    cursor.execute(category_insert, category_data)
    
    db.commit()   

    for subcategory in categories_db[category]:
        subcategory_data = (subcategory_id, subcategory, category_id)
        cursor.execute(subcategory_insert, subcategory_data)
        subcategory_id += 1
        db.commit()   
    category_id +=1
db.close()