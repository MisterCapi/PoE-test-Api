import json
import requests

with open("item_queries/fated_prophecies/Hyrri's Demise Sharktooth Arrow Quiver.json", 'r') as f:
    item_query = json.load(f)

base_html = "https://www.pathofexile.com/api/trade/search/Ritual"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

post_request_response = eval(requests.post(base_html, json=item_query, headers=headers).text)

link_to_search = 'https://www.pathofexile.com/trade/search/Ritual/' + post_request_response['id']

item_list = ','.join(post_request_response['result'][:min(10, len(post_request_response['result']))])

get_url = f"https://www.pathofexile.com/api/trade/fetch/{item_list}?query={post_request_response['id']}"
get_request_result = json.loads(requests.get(get_url, headers=headers).text)

price = 0
for result in get_request_result['result']:
    print(result['listing']['price']['amount'], result['listing']['price']['currency'])
    price += result['listing']['price']['amount']

price /= min(10, len(post_request_response['result']))

with open(f"{item_query['query']['name']}_price.txt", 'a') as f:
    f.write(f"{str(price)},")