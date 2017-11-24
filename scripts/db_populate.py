"""Populate the database with records, players and maps from qlrace.com via the qlrace.com api"""
from urllib.request import Request, urlopen
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from qldf.models import Record, Player, Map
from qldf import create_app, db
import json
import os


# When deploying on heroku, limit the number of data rows. Max 10k rows allowed for free.
if os.environ.get('QLDF_CONFIG', 'config.config') == 'config.heroku_config':
    map_limit = 100
else:
    map_limit = None


def get_data_from_url(url):
    req = Request(url)
    req.add_header('User-Agent', 'qldf api script')
    print(f'GET from {url}')
    return json.loads(urlopen(req).read().decode())


def get_data_from_cache(filename):
    try:
        with open(os.path.abspath(f'tmp/{filename}'), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


if not os.path.exists('tmp/'):
    os.mkdir('tmp/')
# Get list of maps, from cached file or the qlrace.com api
maps = get_data_from_cache('maps.txt')
if not maps:
    maps = get_data_from_url('https://qlrace.com/api/maps')['maps']
    with open(os.path.abspath('tmp/maps.txt'), 'w+') as f:
        json.dump(maps, f)
if map_limit:
    maps = maps[:map_limit]
    print('maps limited on heroku')
# For each map get the records, from cached file or the qlrace.com api
records = get_data_from_cache('records.txt')
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
    with open(os.path.abspath('tmp/records.txt'), 'w+') as f:
        json.dump(records, f)
# Get every unique player id and their name
players = get_data_from_cache('players.txt')
if not players:
    players = {}
    for record in records:
        players[record['player_id']] = record['name']
    with open(os.path.abspath('tmp/players.txt'), 'w+') as f:
        json.dump(players, f)
# Insert data into database
app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)
with app.app_context():
    # Insert the maps into the database
    maps_with_new_ids = {}
    for _map in maps:
        new_map = Map(name=_map, author='', workshop_url='')
        db.session.add(new_map)
        db.session.commit()
        maps_with_new_ids[_map] = new_map.id
    # Insert the players into the database
    players_with_new_ids = {}
    for player_id, player_name in players.items():
        new_player = Player(name=player_name, steam_id=player_id)
        db.session.add(new_player)
        db.session.commit()
        players_with_new_ids[player_id] = new_player.id
    # Insert the records into the database
    for record in records:
        new_record = Record(mode=record['mode'],
                            map_id=maps_with_new_ids[record['map']],
                            player_id=players_with_new_ids[str(record['player_id'])],
                            time=record['time'],
                            match_guid=record['match_guid'],
                            date=record['date'])
        db.session.add(new_record)
        db.session.commit()
