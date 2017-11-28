"""
Get steam workshop ids by map name for maps in the database
Arguments:
fromcache -- load maps from tmp/maps.txt instead of the steam workshop
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app
from bs4 import BeautifulSoup
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs

# Append the text to search for
WORKSHOP_SEARCH_URL = "https://steamcommunity.com/workshop/browse/?appid=282440&searchtext="


def get_html_from_url(url):
    req = Request(url)
    req.add_header('User-Agent', 'qldf workshop scraping script')
    return urlopen(req).read().decode()


# If script was started with arg 'fromcache', load maps from tmp/maps.txt
if len(sys.argv) >= 2 and sys.argv[1] == 'fromcache':
    with open('tmp/maps.txt', 'r') as f:
        maps = json.load(f)
    maps = {_map: None for _map in maps}
else:
    # Otherwise load maps from the database
    app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)
    with app.app_context():
        from qldf.root.models import Map
        map_rows = db.session.query(Map).all()
        maps = {row.name: int(row.workshop_item_id) for row in map_rows}
for _map, workshop_id in maps.items():
    if not workshop_id:
        # Search for map name
        html = get_html_from_url(WORKSHOP_SEARCH_URL + _map)
        soup = BeautifulSoup(html, 'html.parser')
        # Find the map name in the search results
        name_div = soup.find('div', {'class': 'workshopItemTitle ellipsis'})
        if name_div:
            # Extract the url from the html
            workshop_item_url = name_div.find_previous('a')['href']
            # Extract the workshop item id from the url
            # https://steamcommunity.com/sharedfiles/filedetails/?id=808465963&searchtext=daanstrafe01
            workshop_id = int(parse_qs(urlparse(workshop_item_url).query)['id'][0])
            maps[_map] = workshop_id
        else:
            # No search results
            maps[_map] = None
    print(f'{_map}:{workshop_id}')

# Save to tmp folder
if not os.path.exists('tmp/'):
    os.mkdir('tmp/')
with open(os.path.abspath('tmp/map_ids.txt'), 'w+') as f:
    json.dump(maps, f)
