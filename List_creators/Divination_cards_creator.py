f = [x.strip() for x in open('C://GitHub/PoE-test-Api/Item_full_lists/Divination_cards_list.txt', 'r').readlines()]
for i in range(len(f)):
    Name = f[i]
    with open(f"C://GitHub/PoE-test-Api/item_queries/divination_cards/{Name}.json", 'w') as a:
        a.write('{"query":{"status":{"option":"online"},"type":"'+Name+'","type":"and","stats":[{"type":"and","filters":[]}],"filters":{"misc_filters":{"filters":{"corrupted":{"option":"false"}}}}},"sort":{"price":"asc"}}')
        a.close()