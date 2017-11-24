"""Custom jinja filters"""
from config.config import RECORD_MODES
from flask import url_for
from jinja2.filters import do_mark_safe


def setup_custom_jinja_filters(app):
    app.jinja_env.filters['format_record_mode'] = format_record_mode
    app.jinja_env.filters['format_record_time'] = format_record_time
    app.jinja_env.filters['format_record_date'] = format_record_date
    app.jinja_env.filters['format_player_name'] = format_player_name


def format_record_mode(mode):
    if mode or mode == 0:
        return RECORD_MODES[mode]
    else:
        return '-'


def format_record_time(time):
    if time:
        minutes = time // 60000
        seconds = (time % 60000) // 1000
        millis = (time % 60000) % 1000
        if minutes == 0:
            return f'{seconds}.{millis}'
        else:
            return f'{minutes}:{seconds}.{millis}'
    else:
        return '-'


def format_record_date(date):
    if date:
        return date.strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        return '-'


def format_player_name(name):
    """Turn the player name into a url to /player/<name>"""
    return do_mark_safe(f"<a href=\"{url_for('root.player', name=name)}\">{name}</a>")
