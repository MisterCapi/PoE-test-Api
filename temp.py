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
currencies_cases = {"Exalted Orb": "exalted",
                    "Blessed Orb": "blessed",
                    "Cartographer's Chisel": "chisel",
                    "Chaos Orb": "chaos",
                    "Chromatic Orb": "chrome",
                    "Divine Orb": "divine",
                    "Gemcutter's Prism": "gcp",
                    "Jeweller's Orb": "jewellers",
                    "Orb of Scouring": "scour",
                    "Orb of Regret": "regret",
                    "Orb of Fusing": "fusing",
                    "Orb of Chance": "chance",
                    "Orb of Alteration": "alt",
                    "Orb of Alchemy": "alch",
                    "Regal Orb": "regal",
                    "Vaal Orb": "vaal"}
for currency_tab in json.loads(requests.get(url).text)['lines']:
    if currencies_cases.get(currency_tab['currencyTypeName']) is not None:
        currency_item = Item(currencies_cases.get(currency_tab['currencyTypeName']),
                             price=currency_tab['receive']['value'],
                             search_id="Q2Q7Cw",
                             category="currency_tradable",
                             query_path="null")
        currency_item.dump_to_database()
    currency_item = Item(currency_tab['currencyTypeName'],
                         price=currency_tab['receive']['value'],
                         search_id=links.get(currency_tab['currencyTypeName']),
                         category="currency",
                         query_path="null")
    currency_item.dump_to_database()
currency_item = Item("chaos",
                     price=1,
                     search_id="5nBdfa",
                     category="currency_tradable",
                     query_path="null")
currency_item.dump_to_database()
connection = sqlite3.connect('database.db')
cursor = connection.cursor()
print_database()
