import os
import time
from item import Item
import temp
while 1:
    for file in os.listdir("item_queries/divination_cards/"):
        name = file.split(".")[0]
        print(name)
        item = Item(name=name, category='card', query_path=f"item_queries/divination_cards/{file}")
        item.get_data_from_api()
        item.dump_to_database()
        time.sleep(12)
    for file in os.listdir("item_queries/fated_prophecies/"):
        name = file.split(".")[0]
        print(name)
        item = Item(name=name, category='Prophecy', query_path=f"item_queries/fated_prophecies/{file}")
        item.get_data_from_api()
        item.dump_to_database()
        time.sleep(12)
    temp.add_currecy_to_database()
