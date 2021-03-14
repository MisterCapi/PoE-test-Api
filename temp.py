import json
import requests
import sqlite3
import pandas as pd
from item import Item


def print_database():
    with connection:
        cursor.execute("SELECT * from items WHERE category='currency_tradable'")
    [print(x) for x in cursor.fetchall()]


url = "https://poe.ninja/api/data/currencyoverview?league=Ritual&type=Currency"
links = pd.read_csv('Item_full_lists/Currency_list.csv', delimiter=',', header=None, index_col=0).to_dict().get(1)

for currency_tab in json.loads(requests.get(url).text)['lines']:
    currency_item = Item(currency_tab['currencyTypeName'],
                         price=currency_tab['receive']['value'],
                         search_id=links.get(currency_tab['currencyTypeName']),
                         category="currency",
                         query_path="null")
    currency_item.dump_to_database()
currency_item = Item("Chaos Orb",
                     price=1,
                     search_id="5nBdfa",
                     category="currency",
                     query_path="null")
currency_item.dump_to_database()
connection = sqlite3.connect('database.db')
cursor = connection.cursor()
print_database()
