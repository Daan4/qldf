"""Background tasks to be run periodically or when invoked"""
import json
from urllib.request import Request, urlopen

from flask import current_app

from qldf import db
from qldf.models import Server


def get_data_from_url(url, params=None):
    # Don't pass params via urlencode and data,
    # Manually edit the url
    # The api only responds to GET requests
    url += '?'
    for key, value in params.items():
        url += str(key) + '=' + str(value) + '&'
    if url[-1] in '&?':
        url = url[:-1]
    req = Request(url)
    req.add_header('User-Agent', 'qldf.com worker')
    req.add_header('Accept', 'application/json')
    return json.loads(urlopen(req).read().decode())


def update_servers():
    with db.app.app_context():
        # Retrieve a dict of all servers
        current_app.logger.info('Task: Updating servers...')
        server_api_url = current_app.config['SYNCORE_SERVERS_URL']
        params = {'serverKeywords': 'qlrace.com',
                  'hasPassword': 'false'}
        data = get_data_from_url(server_api_url, params)
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
        current_app.logger.info('Task: Servers updated!')


def update_players():
    pass


def update_maps():
    pass

