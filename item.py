import json
import sqlite3
import warnings

import requests

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
league = json.loads(requests.get("https://www.pathofexile.com/api/trade/data/leagues", headers=headers).text)['result'][0]['id']


class Item:

    def __init__(self, name, price=0, search_id=None, category='item'):
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
        """
        self.name = name

        self.price = price
        self.search_id = search_id
        self.category = category

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
                                                  category text)""")

        item_dict = {'name': self.name,
                     'price': self.price,
                     'search_id': self.search_id,
                     'category': self.category}

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
                                                       category=:category
                                                       WHERE name=:name""", item_dict)
                print(f"{self.name:<45} was updated in the database")
        else:
            # Insert if item not in database
            with connection:
                cursor.execute("INSERT INTO items VALUES (:name, :price, :search_id, :category)", item_dict)
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
        else:
            warnings.warn(f"{self.name} is not in the database", RuntimeWarning)


# Demo
item = Item(name="Eternity Shroud", price=20, search_id="b0p8ezSL", category='item')
item.dump_to_database()
item.load_from_database()
print(item.search_link)
# with connection:
#     cursor.execute('select * from items')
# print(cursor.fetchall())