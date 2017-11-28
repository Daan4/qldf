"""Update each workshop item in the database by fetching data from the steam workshop.
Arguments:
fromcache -- try loading workshopitems from cache"""
import sys
import json
import os
from bs4 import BeautifulSoup
from xml.etree.ElementTree import fromstring, ElementTree
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath('..'))
from qldf import db, create_app
from qldf.root.models import WorkshopItem


# Append the workshop item id
WORKSHOP_ITEM_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id="


def get_html_from_url(url):
    req = Request(url)
    print(f'GET from url:{url}')
    req.add_header('User-Agent', 'qldf workshop scraping script')
    return urlopen(req).read().decode()


print('DB: Update workshop item rows')
# If script was started witha arg 'fromcache', try loading data from tmp/workshopitems.txt
fromcache = False
if len(sys.argv) >= 2 and sys.argv[1] == 'fromcache':
    try:
        with open('tmp/workshopitems.txt', 'r') as f:
            workshop_items = json.load(f)
        fromcache = True
    except FileNotFoundError:
        pass

app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)

if fromcache:
    for _id, values_dict in workshop_items.items():
        with app.app_context():
            query = db.session.query(WorkshopItem).\
                filter(WorkshopItem.id == _id).\
                update(values_dict)
            db.session.commit()
else:
    # Get workshop item ids from the database
    with app.app_context():

        workshop_items= db.session.query(WorkshopItem.id, WorkshopItem.item_id).all()
    workshop_items_dict = {item.id: {'item_id': item.item_id} for item in workshop_items}
    custom_url_steam_id = {}
    for item in workshop_items:
        # Get steam workshop page soup
        html = get_html_from_url(WORKSHOP_ITEM_URL + item.item_id)
        soup = BeautifulSoup(html, 'html.parser')
        # find item name
        name = soup.find('div', {'class': 'workshopItemTitle'})
        if name:
            name = name.text
        # find item author
        author_url = soup.find('a', {'class': 'friendBlockLinkOverlay'})
        if author_url:
            author_url = author_url['href']
        # Check if url is steam64 id or custom url
        path = urlparse(author_url).path.split('/')
        if path[1] == 'profiles':
            author_id = path[2]
        else:
            # fetch the steam64 id belonging to the author url
            try:
                author_id = custom_url_steam_id[author_url]
            except KeyError:
                xml = get_html_from_url(author_url + '/?xml=1')
                root = ElementTree(fromstring(xml)).getroot()
                author_id = None
                for child in root:
                    if child.tag == 'steamID64':
                        author_id = child.text
                        break
                custom_url_steam_id[author_url] = author_id
        # find item description
        description = soup.find('div', {'class': 'workshopItemDescription'})
        if description:
            description = description.get_text(separator='\n')
        # find item date and size
        div = soup.find('div', {'class': 'detailsStatsContainerRight'})
        subdivs = div.find_all('div', {'class': 'detailsStatRight'})
        size = subdivs[0].text.split(' ')[0]
        date_text = subdivs[1].text
        # Parse date text, assumed format 'dd nov @ 12:00am' or 'dd nov, yyyy @ 12:00am', where nov is a three day month
        try:
            if ',' in date_text:
                date = datetime.strptime(date_text, '%d %b, %Y @ %I:%M%p')
            else:
                date = datetime.strptime(date_text, '%d %b @ %I:%M%p')
                date = date.replace(year=datetime.now().year)
        except ValueError:
            # When deploying on heroku date format is american ie Oct 20th instead of 20th oct
            if ',' in date_text:
                date = datetime.strptime(date_text, '%b %d, %Y @ %I:%M%p')
            else:
                date = datetime.strptime(date_text, '%b %d @ %I:%M%p')
                date = date.replace(year=datetime.now().year)
        # Default steam time seems to be UTC-8 ->  add 8 hours to get UTC time to store
        date += timedelta(hours=8)
        date = date.isoformat()
        # find item num comments
        num_comments = soup.find_all('span', {'class': 'tabCount'})[1]
        if num_comments:
            num_comments = num_comments.text
        # find item score and number of scores
        num_ratings = soup.find('div', {'class': 'numRatings'})
        if num_ratings:
            num_ratings = num_ratings.text.split(' ')[0]
        else:
            num_ratings = 0
        div = soup.find('div', {'class': 'fileRatingDetails'})
        score_image_url = div.find_next('img')['src']
        score_image_filename = urlparse(score_image_url).path.split('/')[-1]
        score = 0
        for i in range(5):
            if str(i) in score_image_filename:
                score = i
        # find preview image url
        preview_url = soup.find('img', {'class': 'workshopItemPreviewImageEnlargeable'})['src']
        # Update record in database
        values_dict = {'name': name,
                       'author_steam_id': author_id,
                       'description': description,
                       'date': date,
                       'size': size,
                       'num_comments': num_comments,
                       'score': score,
                       'num_scores': num_ratings,
                       'preview_url': preview_url}
        with app.app_context():
            db.session.query(WorkshopItem).\
                filter(WorkshopItem.id == item.id).\
                update(values_dict)
            db.session.commit()
        # Update dict
        workshop_items_dict[item.id].update(values_dict)
    # Write to cache
    if not os.path.exists('tmp/'):
        os.mkdir('tmp/')
    with open(os.path.abspath('tmp/workshopitems.txt'), 'w+') as f:
        json.dump(workshop_items_dict, f)
print('DB: workshop items updated')
