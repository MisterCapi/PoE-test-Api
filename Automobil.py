import bs4
import requests
base_html = "https://pathofexile.gamepedia.com/List_of_divination_cards"
req = requests.get(base_html).text
dataGet = bs4.BeautifulSoup(req, "html5lib")

match = dataGet.find_all('span', class_='divicard-header')
final_List = []
for i in range(len(match)):
    print(match[i].text)
    final_List.append(match[i].text)
with open("Item_full_lists/Divination_cards_list.txt", 'a') as f:
    for i in range(len(final_List)):
        f.write(final_List[i]+"\n")