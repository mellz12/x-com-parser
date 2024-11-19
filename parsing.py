import time
import requests
from bs4 import BeautifulSoup
import json
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

def convert_date(date_str):
    months = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
    }

    day, month_str, year = date_str.split()
    month = months[month_str]
    new_date_str = f"{year}-{month}-{day}"

    return new_date_str



def item_parser(item_link, subcategory_id, db, cursor):

    cur_date = datetime.today()
    cur_date = cur_date.strftime("%Y-%m-%d")

    product_insert = "INSERT INTO products VALUES (%s, %s, %s)"
    productphoto_insert = "INSERT INTO productphoto (photo_url, product_url) VALUES (%s, %s)"
    productratings_insert = "INSERT INTO productratings (username, rating, creation_date, comment, plus, minus, product_id, date_of_pars) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    productcategory_insert = "INSERT INTO productcategory (product_id, subcategory_id) VALUES (%s, %s)"
    productcharacteristics_insert = (
        "INSERT INTO productcharacteristics (value, product_id, characteristic_id) VALUES (%s, %s, %s)"
    )
    productprice_insert = "INSERT INTO productprice (price, product_id, date_of_pars) VALUES (%s, %s, %s)"

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
        print("Ошибка при добавлении товара, возможно он уже добавлен", e)
        db.rollback

    productcategory_data = (id, subcategory_id)
    try:
        cursor.execute(productcategory_insert, productcategory_data)
        db.commit()
    except mysql.connector.Error as e:
        print("Ошибка при добавлении в таблицу productcategory", e)
        db.rollback

    price = soup.find("div", class_="card-content-total-price__current").text
    price = "".join(filter(str.isdecimal, price))

    productprice_data = (price, id, cur_date)
    try:
        cursor.execute(productprice_insert, productprice_data,)
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
        plus, minus, comment = '', '', ''
        username = block.find("div", class_="card-reviews-item-head__name").text
        # print("Пользователь - " ,username)
        date = block.find('div', class_='card-reviews-item-head__date').text
        date = convert_date(date)
        # print("Дата - ", date)
        stars = block.find_all("div", class_="card-reviews-item-head__star active")
        stars = len(stars)
        # print("Количество звёзд - ", stars)
        block_titles = block.find_all('div', class_="card-reviews-item-details-info")
        for block_title in block_titles:
            title = block_title.find('div', class_='card-reviews-item-details-info__title').text.strip()
            if title == "Достоинства":
                plus = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                # print("Плюсы - ", plus)
            elif title == "Недостатки":
                minus = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                # print("Минусы - ", minus)
            else:
                comment = block_title.find('div', class_='card-reviews-item-details-info__value').text.strip()
                # print("Комментарий - ", comment)
        productratings_data = (username, stars, date, comment, plus, minus, id, cur_date)
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
        
        cur_charac_select = "SELECT value FROM productcharacteristics WHERE product_id = %s AND characteristic_id = %s"
        cur_charac_data = (id, charac_id)
        try:
            cursor.execute(cur_charac_select, cur_charac_data)
            cur_charac = cursor.fetchone()
            cur_charac = str(cur_charac[0])
        except (mysql.connector.Error, TypeError) as e:
            # print("Ошибка при получении текущего значения характеристики", e)
            cur_charac = value
        if value != cur_charac:
            cur_charac_update = "UPDATE productcharacteristics SET value = %s WHERE product_id = %s AND characteristic_id = %s"
            cur_charac_update_data = (value, id, charac_id)
            try:
                cursor.execute(cur_charac_update, cur_charac_update_data)
                db.commit()
                print("Характеристика товара ", name, "обновлена")
                time.sleep(10)
            except mysql.connector.Error as e:
                print('Ошибка при обновлении характеристики', e)
                db.rollback
        else:
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
cursor = db.cursor(buffered=True)



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
