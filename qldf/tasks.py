"""Background tasks to be run periodically or when invoked"""
import json
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse
from flask import current_app
from qldf import db
from qldf.models import Server, Player, Map, WorkshopItem
from datetime import datetime, timedelta
from xml.etree.ElementTree import fromstring, ElementTree
from bs4 import BeautifulSoup


def qldf_task(wrapped_task):
    """Log start and end of task and any errors and supply app context"""
    def wrapper():
        with db.app.app_context():
            current_app.logger.info(f'Task {wrapped_task.__name__} starting.')
            try:
                return_value = wrapped_task()
            except Exception as e:
                import traceback
                current_app.logger.error(f'Task {wrapped_task.__name__} failure: {traceback.format_exc()}')
                return None
            current_app.logger.info(f'Task {wrapped_task.__name__} complete.')
            return return_value
    return wrapper


def get_data_from_url(url, _json=False, params=None):
    # Don't pass params via urlencode and data,
    # Manually edit the url
    # The api only responds to GET requests
    if params:
        url += '?'
        for key, value in params.items():
            url += str(key) + '=' + str(value) + '&'
        if url[-1] in '&?':
            url = url[:-1]
    req = Request(url)
    req.add_header('User-Agent', 'qldf.com worker')
    req.add_header('Accept', 'application/json')
    if _json:
        return json.loads(urlopen(req).read().decode())
    else:
        return urlopen(req).read().decode()


@qldf_task
def update_servers():
    # Retrieve a dict of all servers
    server_api_url = current_app.config['SYNCORE_SERVERS_URL']
    params = {'serverKeywords': 'qlrace.com',
              'hasPassword': 'false'}
    data = get_data_from_url(server_api_url, True, params)
    server_ids = []
    for server in data['servers']:
        server_id = server['serverID']
        server_ids.append(server_id)
        address = server['address']
        country = server['location']['countryName']
        map = server['info']['map']
        max_players = server['info']['maxPlayers']
        name = server['info']['serverName']
        keywords = server['info']['extra']['keywords']
        players = server['players']
        for d in players:
            del d['secsConnected']
        players = json.dumps(players)
        # Check if server with server id exists if yes update, else insert
        server_row = db.session.query(Server).\
            filter(Server.server_id == server_id).\
            first()
        if server_row:
            # Update server rows
            db.session.query(Server).\
                filter(Server.server_id == server_id).\
                update({'server_id': server_id,
                        'address': address,
                        'country': country,
                        'map': map,
                        'max_players': max_players,
                        'players': players,
                        'name': name,
                        'keywords': keywords})
            db.session.commit()
        else:
            new_server = Server(server_id=server_id,
                                address=address,
                                country=country,
                                map=map,
                                max_players=max_players,
                                players=players,
                                name=name,
                                keywords=keywords)
            db.session.add(new_server)
            db.session.commit()
    # Remove any server ids in the database that no longer exist according to syncore
    # Get all server ids
    current_ids = db.session.query(Server.id,
                                   Server.server_id).all()

    ids_to_remove = []
    for ids in current_ids:
        if ids.server_id not in server_ids:
            ids_to_remove.append(ids.id)
    for id in ids_to_remove:
        Server.query.filter(Server.id==id).delete()
        db.session.commit()


@qldf_task
def update_players():
    """Update the name of every player in the database by querying steam by their steam64ID"""
    # Get steam ids
    players = db.session.query(Player.steam_id, Player.name, Player.avatar_url).all()
    for player in players:
        xml = get_data_from_url(current_app.config['STEAMPLAYER_PROFILE_URL']+player.steam_id, params={'xml': 1})
        root = ElementTree(fromstring(xml)).getroot()
        name = None
        avatar_url = None
        for child in root:
            if child.tag == 'steamID':
                name = child.text
            elif child.tag == 'avatarFull':
                avatar_url = child.text
        if name is None:
            # Player appears to not exist anymore?
            # Looks like this happens if steam community profile isnt set up
            # Try looking for name and avatar in the html version, if still can't find any then keep the old ones
            html = get_data_from_url(current_app.config['STEAMPLAYER_PROFILE_URL']+player.steam_id)
            soup = BeautifulSoup(html, 'html.parser')
            name = soup.find('span', {'class': 'actual_persona_name'})
            if name:
                name = name.text
            else:
                name = player.name
                current_app.logger.info(f'Task update_players: can\'t find name for player {player.steam_id}')
            avatar_div = soup.find('div', {'class': 'playerAvatarAutoSizeInner'})
            if avatar_div:
                avatar_url = avatar_div.find_next('img')['src']
            else:
                avatar_url = player.avatar_url
        # Update player name and avatar url
        db.session.query(Player).\
            filter(Player.steam_id == player.steam_id).\
            update({'name': name,
                    'avatar_url': avatar_url})
        db.session.commit()


@qldf_task
def update_workshop_items():
    """Update the workshop data for every workshopitem"""
    # Get all maps without a workshopitem and try finding one
    maps_without_workshopitem = db.session.query(Map).\
        filter(Map.workshop_item_id is None).\
        all()
    for _map in maps_without_workshopitem:
        html = get_data_from_url(current_app.config['STEAMWORKSHOP_SEARCH_URL']+_map.name)
        soup = BeautifulSoup(html, 'html.parser')
        # Find the map name in the search results
        name_div = soup.find('div', {'class': 'workshopItemTitle ellipsis'})
        if name_div:
            # Extract the workshopitem url from the html
            workshop_item_url = name_div.find_previous('a')['href']
            # Extract the workshop item id from the url
            workshop_id = int(parse_qs(urlparse(workshop_item_url).query)['id'][0])
            # Create a new empty workshopitem and link it to the map
            new_workshop_item = WorkshopItem(item_id=workshop_id)
            db.session.add(new_workshop_item)
            db.session.commit()
            db.session.query(Map).\
                filter(Map.id == _map.id).\
                update({'workshop_item_id': workshop_id})
            db.session.commit()
    # Update all workshop items. If no new data can be found keep the old data
    # Atm score and num ratings will be set to 0 while other data is kept the same in thes second case
    workshop_items = db.session.query(WorkshopItem).all()
    for item in workshop_items:
        html = get_data_from_url(current_app.config['STEAMWORKSHOP_ITEM_URL'] + item.item_id)
        soup = BeautifulSoup(html, 'html.parser')
        # find item name
        name = soup.find('div', {'class': 'workshopItemTitle'})
        if name:
            name = name.text
        else:
            name = item.name
            current_app.logger.info(f'Task update_workshop_items: can\'t find name for item {item.item_id}')
        # find item author steam64ID
        author_url = soup.find('a', {'class': 'friendBlockLinkOverlay'})
        author_id = None
        if author_url:
            author_url = author_url['href']
            # Check if url is steam64 id or custom url
            path = urlparse(author_url).path.split('/')
            if path[1] == 'profiles':
                author_id = path[2]
            else:
                # fetch the steam64 id belonging to the author url
                xml = get_data_from_url(author_url + '/?xml=1')
                root = ElementTree(fromstring(xml)).getroot()
                author_id = None
                for child in root:
                    if child.tag == 'steamID64':
                        author_id = child.text
                        break
        if not author_id:
            author_id = item.author_steam_id
        # find item description
        description = soup.find('div', {'class': 'workshopItemDescription'})
        if description:
            description = description.get_text(separator='\n')
        else:
            description = item.description
        # find item date and size
        div = soup.find('div', {'class': 'detailsStatsContainerRight'})
        date = None
        size = None
        if div:
            subdivs = div.find_all('div', {'class': 'detailsStatRight'})
            if subdivs:
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
        if date:
            date += timedelta(hours=8)
            date = date.isoformat()
        else:
            date = item.date
        if not size:
            size = item.size
        # find item num comments
        num_comments = soup.find_all('span', {'class': 'tabCount'})[1]
        if num_comments:
            num_comments = num_comments.text
        else:
            num_comments = item.num_comments
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
        if not preview_url:
            preview_url = item.preview_url
        db.session.query(WorkshopItem).\
            filter(WorkshopItem.id == item.id).\
            update({'name': name,
                    'author_steam_id': author_id,
                    'description': description,
                    'date': date,
                    'size': size,
                    'num_comments': num_comments,
                    'score': score,
                    'num_scores': num_ratings,
                    'preview_url': preview_url})
        db.session.commit()
