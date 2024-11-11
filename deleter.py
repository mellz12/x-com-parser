import mysql.connector


config = {
    "user": "root",
    "password": "",
    "host": "127.0.0.1",
    "database": "x-com",
    "raise_on_warnings": True,
}

db = mysql.connector.connect(**config)
cursor = db.cursor()
all_deleter = '''
TRUNCATE characteristicsgroups;
ALTER TABLE characteristicsgroups AUTO_INCREMENT = 1;
TRUNCATE characteristics;
ALTER TABLE characteristics AUTO_INCREMENT = 1;
TRUNCATE productcategory;
ALTER TABLE productcategory AUTO_INCREMENT = 1;
TRUNCATE productcharacteristics;
ALTER TABLE productcharacteristics AUTO_INCREMENT = 1;
TRUNCATE productphoto;
ALTER TABLE productphoto AUTO_INCREMENT = 1;
TRUNCATE productprice;
ALTER TABLE productprice AUTO_INCREMENT = 1;
TRUNCATE productratings;
ALTER TABLE productratings AUTO_INCREMENT = 1;
TRUNCATE products;
ALTER TABLE products AUTO_INCREMENT = 1;
TRUNCATE subcategory;
ALTER TABLE subcategory AUTO_INCREMENT = 1;
'''

categories_deleter = '''
TRUNCATE characteristicsgroups;
ALTER TABLE characteristicsgroups AUTO_INCREMENT = 1;
TRUNCATE characteristics;
ALTER TABLE characteristics AUTO_INCREMENT = 1;
TRUNCATE subcategory;
ALTER TABLE subcategory AUTO_INCREMENT = 1;
'''

product_deleter = '''
TRUNCATE productcategory;
ALTER TABLE productcategory AUTO_INCREMENT = 1;
TRUNCATE productcharacteristics;
ALTER TABLE productcharacteristics AUTO_INCREMENT = 1;
TRUNCATE productphoto;
ALTER TABLE productphoto AUTO_INCREMENT = 1;
TRUNCATE productprice;
ALTER TABLE productprice AUTO_INCREMENT = 1;
TRUNCATE productratings;
ALTER TABLE productratings AUTO_INCREMENT = 1;
TRUNCATE products;
ALTER TABLE products AUTO_INCREMENT = 1;
'''

cursor.execute(all_deleter, multi=True)
db.commit