import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.xcom-shop.ru/logitech_k120_199067.html'#, https://www.xcom-shop.ru/deepcool_pf500_886694.html
# html = requests.get("https://www.xcom-shop.ru/deepcool_pf500_886694.html")
html = requests.get(url)

soup = BeautifulSoup(html.text, 'html.parser')

id = soup.find("div", id='product_part_number').text
id = ''.join(filter(str.isdecimal, id))
print(id)

name = soup.find('div', class_='card-sticky__name').text
print(name)

description = soup.find('div', class_= 'card-tabs-content__description')
try:
    description=description.text
except AttributeError:
    print("Описания нет")
    description = ''
finally:
    print(description)

db = {id : []}
product_table = {'product' : {'id' : id, "name" : name, "desc" : description}}
db[id].append(product_table)

price = soup.find('div', class_='card-content-total-price__current').text
price = ''.join(filter(str.isdecimal, price))
price_table = {'productprice' : {'id' : "sql запрос по макс. id + 1", 'price' : price, 'product_id' : id}}

db[id].append(price_table)




with open('parsed.json', 'w', encoding='utf-8') as file:
    json.dump(db, file, indent=4, ensure_ascii=False)