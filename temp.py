import json
import requests
import sqlite3
from item import Item

url = "https://poe.ninja/api/data/currencyoverview?league=Ritual&type=Currency"

for currency_tab in json.loads(requests.get(url).text)['lines']:
    currency_item = Item(currency_tab['currencyTypeName'], price=currency_tab['receive']['value'], search_id="null", category="currency", query_path="null")
    currency_item.dump_to_database()

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

with connection:
    cursor.execute("SELECT * from items WHERE category='currency'")
[print(x) for x in cursor.fetchall()]
