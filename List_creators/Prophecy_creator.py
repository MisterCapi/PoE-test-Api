f = [x.strip() for x in open('Item_full_lists/Prophecies_list.txt', 'r').readlines()]
for i in range(len(f)):
    Name = f[i]
    with open(f"item_queries/fated_prophecies/{Name} Prophecy.json", 'a') as f:
        f.write('{"query":{"status":{"option":"online"},"name":"'+Name+'","type":"Prophecy","stats":[{"type":"and","filters":[]}],"filters":{"misc_filters":{"filters":{"corrupted":{"option":"false"}}}}},"sort":{"price":"asc"}}')