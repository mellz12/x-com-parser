import time
import requests
from bs4 import BeautifulSoup
import json
import mysql.connector
from mysql.connector import errorcode


def item_parser(item_link, subcategory_id, db, cursor):

    with open("./characteristics.json", "r", encoding="utf-8") as file:
        characteristics_dict = json.load(file)

    product_insert = "INSERT INTO products VALUES (%s, %s, %s)"
    productphoto_insert = "INSERT INTO productphoto (photo_url, product_url) VALUES (%s, %s)"
    productratings_insert = "INSERT INTO productratings (username, rating, creation_date, comment, plus, minus, product_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
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
        print('------------------------------------------------')
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

    reviews_blocks = soup.find_all('div', class_='card-reviews-item')
    for block in reviews_blocks:
        plus = ''
        minus = ''
        comment = ''
        username = block.find("div", class_="card-reviews-item-head__name").text
        print("Пользователь - " ,username)
        date = block.find('div', class_='card-reviews-item-head__date').text
        print("Дата - ", date)
        stars = block.find_all("div", class_="card-reviews-item-head__star active")
        stars = len(stars)
        print("Количество звёзд - ", stars)
        block_titles = block.find_all('div', class_="card-reviews-item-details-info")
        for block_title in block_titles:
            title = block_title.find('div', class_='card-reviews-item-details-info__title').text.strip()
            if title == "Достоинства":
                plus = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                print("Плюсы - ", plus)
            elif title == "Недостатки":
                minus = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                print("Минусы - ", minus)
            else:
                comment = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                print("Комментарий - ", comment)
        productratings_data = (username, stars, date, comment, plus, minus, id)
        try:
            cursor.execute(productratings_insert, productratings_data)
            db.commit()
        except mysql.connector.Error as e:
            print("Ошибка при добавлении отзывов товара", e)
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
    print('------------------------------------------------')


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
            item_parser(item_link, subcategory_id, db, cursor)

        subcategory_id += 1
    category_id += 1
