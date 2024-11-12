import requests
from bs4 import BeautifulSoup
import time
import json
import os
import mysql.connector
from mysql.connector import errorcode

url = 'https://www.xcom-shop.ru/catalog/kompyuternye_komplektyyuschie/'
url_orig = 'https://www.xcom-shop.ru'


config = {'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'x-com',
  'raise_on_warnings': True}

db = mysql.connector.connect(**config)
cursor = db.cursor()

category_id = 1
subcategory_id = 1
category_insert = ("INSERT INTO category (category_name) VALUES (%s)")
subcategory_insert = ("INSERT INTO subcategory (subcategory_name, category_id) VALUES (%s, %s)")
characteristic_insert = ("INSERT INTO characteristics (characteristics_name, subcategory_id) VALUES (%s, %s)")

html = requests.get(url)
soup = BeautifulSoup(html.text, 'html.parser')

if os.path.exists("./categories.json"):
    with open("./categories.json", "r", encoding="utf-8") as file:
        category_db = json.load(file)
else:
    category_db = {}

if os.path.exists("./characteristics.json"):
    with open("./characteristics.json", "r", encoding="utf-8") as file:
        characteristics_db = json.load(file)
else:
    characteristics_db = {}

categories_list = soup.find('div', class_='header-catalog-menu')

categories = categories_list.find_all('a', href=True)
for category in categories:
    if category_id == 4:
        db.close
        break
    if category.text.strip() in category_db.keys():
        print(f'Категория {category.text.strip()} уже добавлена')
    else:
        print(f"Категория: {category.text.strip()}")
        
        category_db[category.text.strip()] = []
        # Начало MySql запроса 

        category_data = (category.text.strip(),)
        try:
            cursor.execute(category_insert, category_data)
            db.commit()
        except mysql.connector.Error as e:
            print("Ошибка при добавлении категории", e)
            db.rollback
            
        # Конец MySql запроса
        subcategories_link = requests.get(f"{url_orig}{category['href']}")
        subcategories_soup = BeautifulSoup(subcategories_link.text, 'html.parser')

        subcategories = subcategories_soup.find_all('a', class_='list-subfolders__item')
        for subcategory in subcategories:
            if subcategory.text.strip() in category_db[category.text.strip()]:
                print(f"Подкатегория {subcategory.text.strip()} уже добавлена")
            else:
                print(f"Подкатегория: {subcategory.text.strip()}")
                category_db[category.text.strip()].append(subcategory.text.strip())
                characteristics_db[subcategory.text.strip()] = []

                # Начало MySql запроса

                subcategory_data = (subcategory.text.strip(), category_id)
                try:
                    cursor.execute(subcategory_insert, subcategory_data)
                    db.commit()
                except mysql.connector.Error as e:
                    print("Ошибка при добавлении подкатегории", e)
                    db.rollback

                # Конец MySql запроса

                items_page = requests.get(f"{url_orig}{subcategory['href']}")
                items_page_soup = BeautifulSoup(items_page.text, 'html.parser')

                items_cards = items_page_soup.find_all('a', class_='catalog_item__name catalog_item__name--tiles')
                for items in items_cards:
                    item_link = requests.get(f'{url_orig}{items['href']}')
                    item_soup = BeautifulSoup(item_link.text, 'html.parser')

                    characteristics = item_soup.find_all('div', class_='card-tabs-props-list-item__label')
                    for characteristic in characteristics:
                        if characteristic.text.strip() in characteristics_db[subcategory.text.strip()]:
                            continue
                        else:
                            characteristics_db[subcategory.text.strip()].append(characteristic.text.strip())
                            characteristic_data = (characteristic.text.strip(), subcategory_id)
                            try:
                                # Начало MySql запроса

                                cursor.execute(characteristic_insert, characteristic_data)
                                db.commit()
                            except mysql.connector.Error as e:
                                print("Ошибка при добавлении характеристики", e)
                                db.rollback

                                # Конец MySql запроса

            subcategory_id += 1
    category_id +=1
    print('------------------------------------')
    
    with open('characteristics.json', 'w', encoding='utf-8') as file:
        json.dump(characteristics_db, file, indent=4, ensure_ascii=False)

with open('categories.json', 'w', encoding='utf-8') as file:
        json.dump(category_db, file, indent=4, ensure_ascii=False)
print("ГОТОВО")
    
