import requests
from bs4 import BeautifulSoup
import json
import mysql.connector
from mysql.connector import errorcode




def item_parser(url, subcategory, subcategory_id, id_counter):

    with open('./characteristics.json', 'r', encoding='utf-8') as file:
        characteristics_dict = json.load(file)
    product_insert = ("INSERT INTO category VALUES (%s, %s, %s)")
    productcategory_insert = ("INSERT INTO category VALUES (%s, %s, %s)")
    productcharacteristics_insert = ("INSERT INTO category VALUES (%s, %s, %s, %s)")
    productprice_insert = ("INSERT INTO category VALUES (%s, %s, %s)")

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    id = soup.find("div", id='product_part_number').text
    id = ''.join(filter(str.isdecimal, id))
    print(id)

    name = soup.find('div', class_='card-sticky__name').text
    description = soup.find('div', class_= 'card-tabs-content__description')

    try:
        description=description.text
    except AttributeError:
        description = ''
    finally:
        print(description)

    product_data = (id, name, description)
    try:
        cursor.execute(product_insert, product_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении товара", e)
        db.rollback

    productcategory_data = (id_counter, id, subcategory_id)
    try:
        cursor.execute(productcategory_insert, productcategory_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении в таблицу productcategory", e)
        db.rollback

    db = {id : []}
    product_table = {'product' : {'id' : id, "name" : name, "desc" : description}}
    db[id].append(product_table)

    price = soup.find('div', class_='card-content-total-price__current').text
    price = ''.join(filter(str.isdecimal, price))
    
    productprice_data = (id_counter, price, id)
    try:
        cursor.execute(productprice_insert, productprice_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении в таблицу productprice", e)
        db.rollback

    characteristics = soup.find_all('li', class_='card-tabs-props-list-item')
    for characteristic in characteristics:
        charac = characteristic.find('div', class_='card-tabs-props-list-item__label')
        value = characteristic.find('div', class_='card-tabs-props-list-item__value')
        




    price_and_rating_dict = {'productprice' : {'id' : "sql запрос по макс. id + 1", 'price' : price, 'product_id' : id}}

    db[id].append(price_and_rating_dict)




config = {'user': 'root',
  'password': '',
  'host': '127.0.0.1',
  'database': 'x-com',
  'raise_on_warnings': True}

db = mysql.connector.connect(**config)
cursor = db.cursor()




url = 'https://www.xcom-shop.ru'

html = requests.get(url)
soup = BeautifulSoup(html, 'html.parser')

categories_list = soup.find('div', class_='header-catalog-menu')

category_id = 1
subcategory_id = 1
id_counter = 1

categories = categories_list.find_all('a', href=True)
for category in categories:
        
    subcategories_link = requests.get(f"{url}{category['href']}")
    subcategories_soup = BeautifulSoup(subcategories_link.text, 'html.parser')

    subcategories = subcategories_soup.find_all('a', class_='list-subfolders__item')
    for subcategory in subcategories:

        items_page = requests.get(f"{url}{subcategory['href']}")
        items_page_soup = BeautifulSoup(items_page.text, 'html.parser')

        items_cards = items_page_soup.find_all('a', class_='catalog_item__name catalog_item__name--tiles')
        for items in items_cards:
            item_link = requests.get(f'{url}{items['href']}')
            item_parser(item_link, subcategory, subcategory_id, id_counter)
            id_counter += 1

        subcategory_id += 1
    category_id += 1
                    # item_soup = BeautifulSoup(item_link.text, 'html.parser')

                    # characteristics = item_soup.find_all('div', class_='card-tabs-props-list-item__label')
                    # for characteristic in characteristics:
                    #     characteristic.text.strip() in characteristics_db[subcategory.text.strip()]
                            
# with open('parsed.json', 'w', encoding='utf-8') as file:
#     json.dump(db, file, indent=4, ensure_ascii=False)