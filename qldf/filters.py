"""Custom jinja filters"""
from flask import url_for, current_app, request
from jinja2.filters import do_mark_safe
from sqlalchemy import asc, desc


def setup_custom_jinja_filters(app):
    app.jinja_env.filters['format_record_mode'] = format_record_mode
    app.jinja_env.filters['format_record_time'] = format_record_time
    app.jinja_env.filters['format_record_date'] = format_record_date
    app.jinja_env.filters['format_player_name'] = format_player_name
    app.jinja_env.filters['format_map_name'] = format_map_name
    app.jinja_env.filters['format_sortable_table_header'] = format_sortable_table_header


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


def format_player_name(name):
    """Turn a player name into a url to /player/<name>"""
    return do_mark_safe(f"<a href=\"{url_for('root.player', name=name)}\">{name}</a>")


def format_map_name(name):
    """Turn a map name into a url to /map/<name>"""
    return do_mark_safe(f"<a href=\"{url_for('root._map', name=name)}\">{name}</a>")


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
