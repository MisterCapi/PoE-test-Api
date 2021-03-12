import json
import requests
import sqlite3
from item import Item
# Ide spac potem dokoncze nie chialo mi sie po angliesku myslec
# def convert_to_valute(currency_in_json):
#     if currency_in_json['currencyTypeName'] == 'Blessed Orb':
#         return 'blessed'
#     if currency_in_json['currencyTypeName'] == 'Exalted Orb':
#         return 'exalted'
#     return 'Not_used_in_trades'


url = "https://poe.ninja/api/data/currencyoverview?league=Ritual&type=Currency"
f = open('Item_full_lists/Currency_list.txt', 'a+')
for currency_tab in json.loads(requests.get(url).text)['lines']:
    # if convert_to_valute(currency_tab) != 'Not_used_in_trades':
    #     print(convert_to_valute(currency_tab))
    #     currency_item = Item(currency_tab['currencyTypeName'], price=currency_tab['receive']['value'], search_id="Q2Q7Cw", category="currency", query_path="null")
# We can add type "Not_used_in_trades" as type of items that we can not use to list items
    f.write(currency_tab['currencyTypeName']+",\n")
    currency_item = Item(currency_tab['currencyTypeName'], price=currency_tab['receive']['value'], search_id="null", category="currency", query_path="null")
    currency_item.dump_to_database()

# connection = sqlite3.connect('database.db')
# cursor = connection.cursor()
#
# with connection:
#     cursor.execute("SELECT * from items WHERE category='currency'")
# [print(x) for x in cursor.fetchall()]
