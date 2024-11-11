import time
import requests
from bs4 import BeautifulSoup
import json
import mysql.connector
from mysql.connector import errorcode


def item_parser(item_link, subcategory, subcategory_id, db, cursor):

    with open("./characteristics.json", "r", encoding="utf-8") as file:
        characteristics_dict = json.load(file)

    product_insert = "INSERT INTO products VALUES (%s, %s, %s)"
    productphoto_insert = "INSERT INTO productphoto (photo_url, product_url) VALUES (%s, %s)"
    productcategory_insert = "INSERT INTO productcategory (product_id, subcategory_id) VALUES (%s, %s)"
    productcharacteristics_insert = (
        "INSERT INTO productcharacteristics (value, product_id, characteristic_id) VALUES (%s, %s, %s)"
    )
    productprice_insert = "INSERT INTO productprice (price, product_id) VALUES (%s, %s)"

    html = requests.get(item_link)
    soup = BeautifulSoup(html.text, "html.parser")

    id = soup.find("div", id="product_part_number").text
    id = "".join(filter(str.isdecimal, id))
    print(id)

    name = soup.find("div", class_="card-sticky__name").text
    print(name)

    description = soup.find("div", class_="card-tabs-content__description")
    try:
        description = description.text
    except AttributeError:
        description = ""
    finally:
        print(description)

    product_data = (id, name, description)
    try:
        cursor.execute(product_insert, product_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении товара", e)
        db.rollback
        return

    productcategory_data = (id, subcategory_id)
    try:
        cursor.execute(productcategory_insert, productcategory_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении в таблицу productcategory", e)
        db.rollback

    price = soup.find("div", class_="card-content-total-price__current").text
    price = "".join(filter(str.isdecimal, price))

    productprice_data = (price, id)
    try:
        cursor.execute(productprice_insert, productprice_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении в таблицу productprice", e)
        db.rollback

        img_container = soup.find('div', class_='card-content-image-main-slider')
        image_link = img_container.find('img')
        
        productphoto_data = (image_link['src'], id)
        try:
            cursor.execute(productphoto_insert, productphoto_data)
            db.commit()
        except mysql.connector.Error as e:
            print("Ошибка при добавлении фотографии товара", e)
            db.rollback


    characteristics_table = soup.find("ul", class_="card-tabs-props-list")
    characteristics = characteristics_table.find_all('li')
    for characteristic in characteristics:
        charac = characteristic.find("div", class_="card-tabs-props-list-item__label")
        value = characteristic.find("div", class_="card-tabs-props-list-item__value")
        try:
            charac = charac.text.strip()
            value = value.text.strip()
        except:
            print("Ошибка! Характеристика не найдена")
            charac, value = '', ''
            continue
        finally:
            print(charac, " - ", value)
        
            id_sql = "SELECT id FROM characteristics WHERE subcategory_id = %s AND characteristics_name = %s"
            id_sql_data = (subcategory_id, charac)
        try:
            cursor.execute(id_sql, id_sql_data)
            charac_id = cursor.fetchone()
            charac_id = int(charac_id[0])
        except mysql.connector.Error as e:
            print("Ошибка при получении id", e)

        productcharac_data = (value, id, charac_id)
        try:
            cursor.execute(productcharacteristics_insert, productcharac_data)
            db.commit()
        except mysql.connector.Error as e:
            print("Ошибка при добавлении характеристики товара", e)
            db.rollback

    price_and_rating_dict = {
        "productprice": {
            "id": "sql запрос по макс. id + 1",
            "price": price,
            "product_id": id,
        }
    }


config = {
    "user": "root",
    "password": "",
    "host": "127.0.0.1",
    "database": "x-com",
    "raise_on_warnings": True,
}

db = mysql.connector.connect(**config)
cursor = db.cursor()



url = "https://www.xcom-shop.ru"

html = requests.get(url)
soup = BeautifulSoup(html.text, "html.parser")

categories_list = soup.find("div", class_="header-catalog-menu")

category_id = 1
subcategory_id = 1

categories = categories_list.find_all("a", href=True)
for category in categories:
    if category_id == 4:
        break
    subcategories_link = requests.get(f"{url}{category['href']}")
    subcategories_soup = BeautifulSoup(subcategories_link.text, "html.parser")

    subcategories = subcategories_soup.find_all("a", class_="list-subfolders__item")
    for subcategory in subcategories:

        items_page = requests.get(f"{url}{subcategory['href']}")
        items_page_soup = BeautifulSoup(items_page.text, "html.parser")

        items_cards = items_page_soup.find_all(
            "a", class_="catalog_item__name catalog_item__name--tiles"
        )
        for items in items_cards:
            item_link = url + items["href"]
            item_parser(item_link, subcategory, subcategory_id, db, cursor)

        subcategory_id += 1
    category_id += 1
