import copy
import json
import os
import sqlite3
import warnings
from datetime import datetime
from math import ceil

import requests

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
league = \
json.loads(requests.get("https://www.pathofexile.com/api/trade/data/leagues", headers=headers).text)['result'][0]['id']


class Item:

    def __init__(self, name, price=0, search_id=None, category='item', query_path=None):
        """
        Class representing an item and its economic activities (data is kept in the database, updated from official trade api)

        :param name: name of the item
        :type name: str
        :param price: price of the item (chaos orbs)
        :type price: int
        :param search_id: unique search id
        :type search_id: str
        :param category: 'item' or 'currency'
        :type category: str
        :param query_path: path to the item query
        :type query_path: str
        """
        currencies_cases = {"exalted": "Exalted Orb",
                            "blessed": "Blessed Orb",
                            "chisel": "Cartographer's Chisel",
                            "chaos": "Chaos Orb",
                            "chrome": "Chromatic Orb",
                            "divine": "Divine Orb",
                            "gcp": "Gemcutter's Prism",
                            "jewellers": "Jeweller's Orb",
                            "scour": "Orb of Scouring",
                            "regret": "Orb of Regret",
                            "fusing": "Orb of Fusing",
                            "chance": "Orb of Chance",
                            "alt": "Orb of Alteration",
                            "alch": "Orb of Alchemy",
                            "regal": "Regal Orb",
                            "vaal": "Vaal Orb"}
        if name in currencies_cases:
            self.name = currencies_cases[name]
        else:
            self.name = name
        self.price = price
        self.search_id = search_id
        self.category = category
        self.query_path = query_path

    @property
    def search_link(self):
        """
        Generates a link to the search website

        :return: link to the item search
        :rtype: str
        """
        if self.category == 'item':
            return f"https://www.pathofexile.com/trade/search/{league}/{self.search_id}"
        else:
            return f"https://www.pathofexile.com/trade/exchange/{league}/{self.search_id}"

    def dump_to_database(self):
        """
        Dumps the data to the database
        Either updates the data if item is already present or inserts it
        """
        with connection:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")

        # Create table if doesn't exist
        if not len(cursor.fetchall()):
            cursor.execute("""CREATE TABLE items (name text,
                                                  price real, 
                                                  search_id text,
                                                  category text,
                                                  query_path text)""")

        item_dict = {'name': self.name,
                     'price': self.price,
                     'search_id': self.search_id,
                     'category': self.category,
                     'query_path': self.query_path}

        with connection:
            cursor.execute("SELECT * FROM items WHERE name=:name", item_dict)

        if len(cursor.fetchall()):
            # Update if item in database
            if self.price == 0:
                print(f"{self.name:<45} wasn't updated in the database -- Reason: new data was invalid")
            else:
                with connection:
                    cursor.execute("""UPDATE items SET name=:name,
                                                       price=:price, 
                                                       search_id=:search_id,
                                                       category=:category,
                                                       query_path=:query_path
                                                       WHERE name=:name""", item_dict)
                print(f"{self.name:<45} was updated in the database")
        else:
            # Insert if item not in database
            with connection:
                cursor.execute("INSERT INTO items VALUES (:name, :price, :search_id, :category, :query_path)",
                               item_dict)
            print(f"{self.name:<45} was added to the database")

    def load_from_database(self):
        """
        Loads the item from the database
        """
        with connection:
            cursor.execute("SELECT * FROM items WHERE name=:name", {'name': self.name})

        select_result = cursor.fetchall()

        if select_result:
            self.price = select_result[0][1]
            self.search_id = select_result[0][2]
            self.category = select_result[0][3]
            self.query_path = select_result[0][4]
        else:
            warnings.warn(f"{self.name} is not in the database", RuntimeWarning)

    def get_data_from_api(self):
        """
        Fill all values of the item using a query from 'search_queries'
        The name of the query file in JSON must match the class self.name attribute
        """
        # Load the json query
        if not os.path.exists(self.query_path):
            raise EnvironmentError(
                f"There is no \"{self.query_path}]\" file\nPlease create the query file for {self.name}\n")

        with open(self.query_path, 'r', encoding='utf8') as f:
            query = json.load(f)
        base_html = f"https://www.pathofexile.com/api/trade/search/{league}"
        post_request = eval(requests.post(base_html, json=query, headers=headers).text)
        if post_request:
            self.search_id = post_request['id']
            item_list = ','.join(post_request['result'][:min(10, len(post_request['result']))])
            get_url = f"https://www.pathofexile.com/api/trade/fetch/{item_list}?query={post_request['id']}"
            get_request_result = json.loads(requests.get(get_url, headers=headers).text)

            price = 0
            for result in get_request_result['result']:
                currency_item = Item(name=result['listing']['price']['currency'])
                currency_item.load_from_database()
                price += result['listing']['price']['amount'] * currency_item.price

            self.price = price / min(10, len(post_request['result']))
            print(round(price, 2))

            funished_item = Item
        else:
            warnings.warn("No item listed on site", RuntimeWarning)


# item = Item(name="Item 15", price=20, search_id="b0p8ezSL", category='item', )
# item.dump_to_database()
# item.load_from_database()
# print(item.search_link)
# with connection:
#     cursor.execute("SELECT * from items WHERE name='Exalted Orb'")
# kubus_Puchatek = Item(name='chaos')
# kubus_Puchatek.load_from_database()
# print(kubus_Puchatek.price)
item = Item(name="The Doctor", query_path="item_queries/divination_cards/The Doctor.json")
item.get_data_from_api()
