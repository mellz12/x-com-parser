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

with open("./characteristics.json", 'r', encoding='utf-8') as file:
    characteristics_db = json.load(file)

category_id = 1
subcategory_id = 1
characteristic_id = 1
category_insert = ("INSERT INTO category VALUES (%s, %s)")
subcategory_insert = ("INSERT INTO subcategory VALUES (%s, %s, %s)")
characteristic_insert = ("INSERT INTO charcteristics VALUES (%s, %s, %s)")


for category in categories_db.keys():
    category_data = (category_id, category)
    try:
        cursor.execute(category_insert, category_data)
    except:
        print("Ошибка при добавлении категории")
    
    try:
        db.commit()
    except:
        db.rollback

   

    for subcategory in categories_db[category]:
        subcategory_data = (subcategory_id, subcategory, category_id)
        try:
            cursor.execute(subcategory_insert, subcategory_data)
        except:
            print("Ошибка при добавлении подкатегории")
        subcategory_id += 1

        try:
            db.commit()
        except:
            db.rollback

    if subcategory in characteristics_db.keys():
        for characteristic in characteristics_db[subcategory]:
            characteristic_data = (characteristic_id, characteristic, subcategory_id)
            try:
                cursor.execute(characteristic_insert, characteristic_data)
            except:
                print("Ошибка при добавлении характеристики")
            characteristic_id += 1

            try:
                db.commit()
            except:
                db.rollback


    category_id +=1
db.close()