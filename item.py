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

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
league = json.loads(requests.get("https://www.pathofexile.com/api/trade/data/leagues", headers=headers).text)['result'][0]['id']


# def add_currency_filter_to_query(query, currency):
#     """
#     Adds the currency filter to the query
#
#     :param query: the query dictionary
#     :type query: dict
#     :param currency: currency type
#     :type currency: str
#     :return: the query dictionary
#     :rtype: dict
#     """
#     if "filters" not in query["query"]:
#         query["query"]["filters"] = {}
#     if "trade_filters" not in query["query"]["filters"]:
#         query["query"]["filters"]["trade_filters"] = {}
#     if "filters" not in query["query"]["filters"]["trade_filters"]:
#         query["query"]["filters"]["trade_filters"]["filters"] = {}
#     if "price" not in query["query"]["filters"]["trade_filters"]["filters"]:
#         query["query"]["filters"]["trade_filters"]["filters"]["price"] = {}
#     if "option" not in query["query"]["filters"]["trade_filters"]["filters"]["price"] or \
#             query["query"]["filters"]["trade_filters"]["filters"]["price"]["option"] != currency:
#         query["query"]["filters"]["trade_filters"]["filters"]["price"]["option"] = currency
#
#     return query


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
                cursor.execute("INSERT INTO items VALUES (:name, :price, :search_id, :category, :query_path)", item_dict)
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

    # def get_data_from_api(self):
    #     """
    #     Fill all values of the item using a query from 'search_queries'
    #     The name of the query file in JSON must match the class self.name attribute
    #     """
    #     # Load the json query
    #     if not os.path.exists(self.query_path):
    #         raise EnvironmentError(f"There is no \"{self.query_path}]\" file\nPlease create the query file for {self.name}\n")
    #
    #     with open(self.query_path, 'r', encoding='utf8') as f:
    #         query = json.load(f)
    #
    #     # Create first request to get list of items that fit the query
    #     if self.category == 'item':
    #         # Process item trades
    #         url = f"https://www.pathofexile.com/api/trade/search/{league}"
    #
    #         # Request in chaos orbs
    #         chaos_query = add_currency_filter_to_query(copy.deepcopy(query), "chaos")
    #         chaos_request = json.loads(requests.post(url, json=chaos_query, headers=headers).text)
    #         if 'result' not in chaos_request:
    #             warnings.warn(f"The query for {self.name} (in chaos) returned an invalid response when executed\nCheck if the query is valid",
    #                           category=RuntimeWarning)
    #             chaos_result = {}
    #         else:
    #             num_chaos_trades = min(10, len(chaos_request['result']))
    #             chaos_items = ','.join(chaos_request['result'][:num_chaos_trades])
    #             chaos_id = chaos_request['id']
    #             chaos_result_url = f"https://www.pathofexile.com/api/trade/fetch/{chaos_items}?query={chaos_id}"
    #             chaos_result = json.loads(requests.get(chaos_result_url, headers=headers).text)
    #
    #         # Request in exalted orbs
    #         exalted_query = add_currency_filter_to_query(copy.deepcopy(query), "exalted")
    #         exalted_request = json.loads(requests.post(url, json=exalted_query, headers=headers).text)
    #         if 'result' not in exalted_request:
    #             warnings.warn(f"The query for {self.name} (in exalted) returned an invalid response when executed\nCheck if the query is valid",
    #                           category=RuntimeWarning)
    #             exalted_result = {}
    #         else:
    #             num_exalted_trades = min(10, len(exalted_request['result']))
    #             exalted_items = ','.join(exalted_request['result'][:num_exalted_trades])
    #             exalted_id = exalted_request['id']
    #             exalted_result_url = f"https://www.pathofexile.com/api/trade/fetch/{exalted_items}?query={exalted_id}"
    #             exalted_result = json.loads(requests.get(exalted_result_url, headers=headers).text)
    #
    #         # Calculate the price
    #         # Chaos
    #         chaos_price = 0
    #         if 'result' in chaos_result:
    #             chaos_prices = []
    #             for chaos_offer in chaos_result['result']:
    #                 chaos_prices.append(chaos_offer["listing"]["price"]["amount"])
    #
    #             # Chaos price = avg(avg, median)
    #             mean = sum(chaos_prices) / len(chaos_prices)
    #             median = chaos_prices[int(len(chaos_prices) / 2.0)]
    #             chaos_price = (mean + median) / 2.0
    #
    #         # Exalted
    #         exalted_price = 0
    #         if 'result' in exalted_result:
    #             exalted_prices = []
    #             for exalted_offer in exalted_result['result']:
    #                 exalted_rate = 100 # TODO: read exalted price from somewhere
    #
    #                 exalted_prices.append(exalted_offer["listing"]["price"]["amount"] * exalted_rate)
    #
    #             # Exalted price = avg(avg, median)
    #             mean = sum(exalted_prices) / len(exalted_prices)
    #             median = exalted_prices[int(len(exalted_prices) / 2.0)]
    #             exalted_price = (mean + median) / 2.0
    #
    #         if chaos_price == 0:
    #             chaos_price = exalted_price
    #         chaos_price = ceil(chaos_price)
    #         if exalted_price == 0:
    #             exalted_price = chaos_price
    #         exalted_price = ceil(chaos_price)
    #
    #         self.price = min(chaos_price, exalted_price)
    #         # Original request for search link generation
    #         request = json.loads(requests.post(url, json=query, headers=headers).text)
    #     elif :
    #         # # Process currency trades
    #         # url = f"https://www.pathofexile.com/api/trade/exchange/{self.league}"
    #         # request = json.loads(requests.post(url, json=query, headers=headers).text)
    #         # if 'result' not in request:
    #         #     warnings.warn(f"The query for {self.name} returned an invalid response when executed\nCheck if the query is valid", category=RuntimeWarning)
    #         #     self.price = 0
    #         # else:
    #         #     num_trades = min(10, len(request['result']))
    #         #     items = ','.join(request['result'][:num_trades])
    #         #     result_url = f"https://www.pathofexile.com/api/trade/fetch/{items}?query={request['id']}"
    #         #     result = json.loads(requests.get(result_url, headers=headers).text)
    #         #
    #         #     if 'result' in result:
    #         #         prices = []
    #         #         for offer in result['result']:
    #         #             prices.append(offer["listing"]["price"]["amount"])
    #         #         self.price = int(prices[-1])
    #         #     else:
    #         #         self.price = 100
    #
    #
    #     if 'result' not in request:
    #         warnings.warn(f"The query for {self.name} returned an invalid response when executed\nCheck if the query is valid", category=RuntimeWarning)
    #         self.search_id = "Error"
    #         self.date_checked = datetime.utcnow()
    #     else:
    #         self.search_id = request['id']
    #         self.date_checked = datetime.utcnow()


# Demo
item = Item(name="Item 15", price=20, search_id="b0p8ezSL", category='item', )
item.dump_to_database()
item.load_from_database()
print(item.search_link)
# with connection:
# #     cursor.execute('select * from items')
# # print(cursor.fetchall())