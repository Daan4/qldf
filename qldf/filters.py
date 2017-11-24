"""Custom jinja filters"""
from config.config import RECORD_MODES


def setup_custom_jinja_filters(app):
    app.jinja_env.filters['format_record_mode'] = format_record_mode
    app.jinja_env.filters['format_record_time'] = format_record_time
    app.jinja_env.filters['format_record_date'] = format_record_date


def format_record_mode(mode):
    return RECORD_MODES[mode]


def format_record_time(time):
    minutes = time // 60000
    seconds = (time % 60000) // 1000
    millis = (time % 60000) % 1000
    if minutes == 0:
        return f'{seconds}.{millis}'
    else:
        return f'{minutes}:{seconds}.{millis}'


def format_record_date(date):
    return date.strftime('%Y-%m-%d %H:%M:%S UTC')
