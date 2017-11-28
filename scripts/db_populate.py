"""Populate the database with records, players and maps from qlrace.com via the qlrace.com api
Arguments:
noupdate -- skips updating workshop items at end
"""
import os
import sys
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf.models import Record, Player, Map, WorkshopItem
from qldf import create_app, db
import json
import os
import subprocess
from config import heroku_config

# Get absolute dir for calling subprocesses
scripts_dir = os.path.dirname(__file__)

maps_cache_filepath = os.path.join(scripts_dir, 'tmp/maps.json')
records_cache_filepath = os.path.join(scripts_dir, 'tmp/records.json')
players_cache_filepath = os.path.join(scripts_dir, 'tmp/players.json')
mapids_cache_filepath = os.path.join(scripts_dir, 'tmp/map_ids.json')


# When deploying on heroku, limit the number of data rows. Max 10k rows allowed for free.
if 'config.scripts_config' == 'config.heroku_config':
    map_limit = heroku_config.MAP_LIMIT
else:
    map_limit = None


def get_data_from_url(url):
    req = Request(url)
    print(f'GET from url:{url}')
    req.add_header('User-Agent', 'qldf api script')
    return json.loads(urlopen(req).read().decode())


def get_data_from_cache(path):
    try:
        with open(path, 'r') as _f:
            print(f'GET from cache:{path}')
            return json.load(_f)
    except FileNotFoundError:
        return None


if not os.path.exists(os.path.dirname(maps_cache_filepath)):
    os.mkdir(os.path.dirname(maps_cache_filepath))

# Get list of maps, from cached file or the qlrace.com api
print('Getting map names')
maps = get_data_from_cache(maps_cache_filepath)
if not maps:
    maps = get_data_from_url('https://qlrace.com/api/maps')['maps']
    # limit maps
    if map_limit:
        print(f'Maps limited to {map_limit}')
        maps = maps[:map_limit]
    with open(os.path.abspath(maps_cache_filepath), 'w+') as f:
        json.dump(maps, f)


# For each map get the records, from cached file or the qlrace.com api
print('Getting records')
records = get_data_from_cache(records_cache_filepath)
if not records:
    records = []
    for _map in maps:
        new_records = []
        # vql, no weapons = mode 3
        new_records += get_data_from_url(f'https://qlrace.com/api/map/{_map}?weapons=false&physics=classic')['records']
        # vql, weapons = mode 2
        new_records += get_data_from_url(f'https://qlrace.com/api/map/{_map}?weapons=true&physics=classic')['records']
        # pql, no weapons = mode 1
        new_records += get_data_from_url(f'https://qlrace.com/api/map/{_map}?weapons=false&physics=turbo')['records']
        # pql, weapons = mode 0
        new_records += get_data_from_url(f'https://qlrace.com/api/map/{_map}?weapons=true&physics=turbo')['records']
        # add the map name to every record
        for i in range(len(new_records)):
            new_records[i]['map'] = _map
        records += new_records
    with open(os.path.abspath(records_cache_filepath), 'w+') as f:
        json.dump(records, f)

# Get every unique player id and their name
print('Getting players')
players = get_data_from_cache(players_cache_filepath)
if not players:
    players = {}
    for record in records:
        players[record['player_id']] = record['name']
    with open(os.path.abspath(players_cache_filepath), 'w+') as f:
        json.dump(players, f)
print('Getting workshop item ids for maps')

# Get workshop item ids for maps from cache or by searching the steam workshop for map names
maps_with_workshop_ids = get_data_from_cache(mapids_cache_filepath)
if not maps_with_workshop_ids:
    subprocess.call(['python', f'{scripts_dir}/get_map_workshop_ids.py', 'fromcache'])
    maps_with_workshop_ids = get_data_from_cache(mapids_cache_filepath)

# Insert data into database
app = create_app('config.scripts_config')
with app.app_context():
    # Insert the workshop items into the database
    print('DB: inserting workshop items')
    unique_workshop_ids = set(maps_with_workshop_ids.values())
    workshop_items_new_ids = {}
    for _id in unique_workshop_ids:
        if _id:
            new_workshop_item = WorkshopItem(item_id=_id)
            db.session.add(new_workshop_item)
            db.session.commit()
            workshop_items_new_ids[_id] = new_workshop_item.id

    # Insert the maps into the database
    print('DB: inserting maps')
    maps_with_new_ids = {}
    for _map in maps:
        try:
            new_map = Map(name=_map,
                          workshop_item_id=workshop_items_new_ids[maps_with_workshop_ids[_map]])
        except KeyError:
            new_map = Map(name=_map,
                          workshop_item_id=None)
        db.session.add(new_map)
        db.session.commit()
        maps_with_new_ids[_map] = new_map.id

    # Insert the players into the database
    print('DB: inserting players')
    players_with_new_ids = {}
    for player_id, player_name in players.items():
        new_player = Player(name=player_name,
                            steam_id=player_id)
        db.session.add(new_player)
        db.session.commit()
        players_with_new_ids[player_id] = new_player.id

    # Insert the records into the database
    print('DB: inserting records')
    for record in records:
        # player_with_new_ids keys can be an int or a str
        # seems to depend on if they were loaded from cache or from the api
        try:
            player_id = players_with_new_ids[str(record['player_id'])]
        except KeyError:
            player_id = players_with_new_ids[int(record['player_id'])]
        new_record = Record(mode=record['mode'],
                            map_id=maps_with_new_ids[record['map']],
                            player_id=player_id,
                            time=record['time'],
                            match_guid=record['match_guid'],
                            date=record['date'])
        db.session.add(new_record)
    db.session.commit()
    # Create workshop items
# Update workshop items by calling db_update_workshopitems.
if not(len(sys.argv) >= 2 and sys.argv[1] == 'noupdate'):
    subprocess.call(['python', f'{scripts_dir}/db_update_workshopitems.py', 'fromcache'])
else:
    print('noupdate -- not updating workshop items')
print('DB populated')
