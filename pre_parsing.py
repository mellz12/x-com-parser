import requests
from bs4 import BeautifulSoup
import time
import json
import os

url = 'https://www.xcom-shop.ru/catalog/kompyuternye_komplektyyuschie/'
url_orig = 'https://www.xcom-shop.ru'

html = requests.get(url)
soup = BeautifulSoup(html.text, 'html.parser')

if os.path.exists("./categories.json"):
    # файл существует
    with open("./categories.json", "r", encoding="utf-8") as file:
        category_db = json.load(file)
else:
    category_db = {}

if os.path.exists("./characteristics.json"):
    # файл существует
    with open("./characteristics.json", "r", encoding="utf-8") as file:
        characteristics_db = json.load(file)
else:
    characteristics_db = {}

categories_list = soup.find('div', class_='header-catalog-menu')

categories = categories_list.find_all('a', href=True)
for category in categories:
    if category.text.strip() in category_db.keys():
        print(f'Категория {category.text.strip()} уже добавлена')
    else:
        print(f"Категория: {category.text.strip()}")
        
        category_db[category.text.strip()] = []
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
            print('------------------------------------')
    
    with open('characteristics.json', 'w', encoding='utf-8') as file:
        json.dump(characteristics_db, file, indent=4, ensure_ascii=False)
                
    time.sleep(1)

with open('categories.json', 'w', encoding='utf-8') as file:
        json.dump(category_db, file, indent=4, ensure_ascii=False)

print("ГОТОВО")
    
