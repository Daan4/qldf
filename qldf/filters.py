"""Custom jinja filters"""
from flask import url_for, current_app, request
from jinja2.filters import do_mark_safe
import re


def setup_custom_jinja_filters(app):
    app.jinja_env.filters['format_record_mode'] = format_record_mode
    app.jinja_env.filters['format_record_time'] = format_record_time
    app.jinja_env.filters['format_record_date'] = format_record_date
    app.jinja_env.filters['format_player_name'] = format_player_name
    app.jinja_env.filters['format_map_name'] = format_map_name
    app.jinja_env.filters['format_sortable_table_header'] = format_sortable_table_header
    app.jinja_env.filters['format_workshop_url'] = format_workshop_url
    app.jinja_env.filters['format_profile_url'] = format_profile_url
    app.jinja_env.filters['print_newlines'] = print_newlines
    app.jinja_env.filters['format_players'] = format_players
    app.jinja_env.filters['format_server'] = format_server
    app.jinja_env.filters['strip_colors'] = strip_colors


def format_players(players):
    """Format list of players dicts as html
    input format:
    [{name: <string>, score: <int>, totalconnected: <string>}], 1 dict per player"""
    if players:
        html_output = '<table><tr><th>Name</th><th>Time</th><th>Connected for</th></tr>'
        for player in players:
            # format time
            if player['score'] == 2147483647:
                player['score'] = '-'
            else:
                player['score'] = format_record_time(player['score'])
            html_output += f"<tr><td>{strip_colors(player['name'])}</td><td>{player['score']}</td><td>{player['totalConnected']}</td></tr>"
        html_output += '</table>'
    else:
        html_output = ''
    return do_mark_safe(html_output)


def format_record_mode(mode):
    if mode or mode == 0:
        return current_app.config['RECORD_MODES'][mode]
    else:
        return '-'


def format_record_time(time):
    if time:
        minutes = time // 60000
        seconds = (time % 60000) // 1000
        millis = (time % 60000) % 1000
        if minutes == 0:
            return f'{seconds}.{str(millis).zfill(3)}'
        else:
            return f'{minutes}:{str(seconds).zfill(2)}.{str(millis).zfill(3)}'
    else:
        return '-'


def format_record_date(date):
    if date:
        return date.strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        return '-'


def format_workshop_url(item_id):
    """Turn a steam workshop item id into a workshop item link"""
    if not item_id:
        return '-'
    else:
        base_url = current_app.config['STEAMWORKSHOP_ITEM_URL']
        return do_mark_safe(f"<a href=\"{base_url}{item_id}\">link</a>")


def format_profile_url(steam_id):
    """Turn a steam64 id into a steam profile link"""
    base_url = current_app.config['STEAMPLAYER_PROFILE_URL']
    return do_mark_safe(f"<a href=\"{base_url}{steam_id}\">link</a>")


def format_player_name(name, steam_id):
    """Turn a player name into a url to /player/<steam_id>"""
    return do_mark_safe(f"<a href=\"{url_for('root.player', steam_id=steam_id)}\">{name}</a>")


def strip_colors(name):
    """Remove quake name colors from player name."""
    return re.sub(r'\^[0-9]', '', name)


def format_server(name, address):
    """Turn a ql server ip address into a clickable link that launches ql and connects to the address"""
    return do_mark_safe(f"<a href=\"steam://connect/{address}\">{name}</a>")


def format_map_name(name):
    """Turn a map name into a url to /map/<name>"""
    return do_mark_safe(f"<a href=\"{url_for('root._map', name=name)}\">{name}</a>")


def print_newlines(string):
    """Print \n in string as newlines."""
    return do_mark_safe(string.replace('\n', '<br/>'))


def format_sortable_table_header(header, sortby, sortdir, reverse_sortdir_on, **kwargs):
    """Sort a table by the database field db_field, direction is 'asc', 'desc' or None
    Args:
        header (str): Table header
        sortby (str): Database field to sorty by
        sortdir (str): Direction to sort in, either 'asc' or 'desc'
        reverse_sortdir_on (str): The name of a database field to sort in the opposite direction of sortdir
        **kwargs: Any keyword arguments to be used in url_for
        """
    if reverse_sortdir_on == sortby:
        if sortdir == 'asc':
            sortdir = 'desc'
        else:
            sortdir = 'asc'
    return do_mark_safe(f"<a href=\"{url_for(request.endpoint, sortby=sortby, sortdir=sortdir, **kwargs)}\">{header}</a>")
