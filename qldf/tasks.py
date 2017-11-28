"""Background tasks to be run periodically or when invoked"""
from urllib.request import Request, urlopen
from flask import current_app
from qldf import db
import json


def get_data_from_url(url, params=None):
    # Don't pass params via urlencode and data,
    # Manually edit the url
    # The api only responds to GET requests
    url += '?'
    for key, value in params.items():
        url += str(key) + '=' + str(value) + '&'
    if url[-1] == '&':
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
        params = {'serverKeywords': 'qlrace.com'}
        data = get_data_from_url(server_api_url, params)
        data = 1
        current_app.logger.info('Task: Servers updated!')


def update_players():
    pass


def update_maps():
    pass

