from flask import Blueprint, render_template, session, url_for, g, request
from time import time
from .models import Player, Record, Map
from config.config import ROWS_PER_PAGE
from sqlalchemy import func, desc
from qldf import db

root = Blueprint('root', __name__, url_prefix='')


@root.route('/')
def index():
    return render_template('index.html')


@root.route('/servers/')
def servers():
    return render_template('servers.html')


@root.route('/player/<string:name>/', defaults={'page': 1})
@root.route('/player/<string:name>/<int:page>')
def player(page, name):
    """Show records and stats for a single player"""
    pagination = db.session.query(Record.mode,
                                  Record.time,
                                  Record.date,
                                  Map.name.label('map_name'),
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Player, Map).\
        order_by(desc(Record.date)).\
        paginate(page, ROWS_PER_PAGE, True)
    return render_template('player.html',
                           title=name,
                           name=name,
                           pagination=pagination)


@root.route('/players/', defaults={'page': 1})
@root.route('/players/page/<int:page>')
def players(page):
    """Show a list of all players and their number of records and world records."""
    # subquery to get all record ranks per player
    sq = db.session.query(Player.id.label('id'),
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Player.records).\
        subquery()
    # subquery to get wr count per player
    sq2 = db.session.query(Player.id.label('id'),
                           func.count(sq.c.id).label('wr_count')).\
        join(sq, sq.c.id == Player.id).\
        filter(sq.c.rank == 1).\
        group_by(Player.id).\
        subquery()
    # subquery to get record count per player
    sq3 = db.session.query(Player.id.label('id'),
                           func.count(Player.id).label('record_count')).\
        join(Player.records).\
        group_by(Player.id).\
        subquery()
    # final query joining record count and wr count
    pagination = db.session.query(Player.id,
                                  Player.name,
                                  Player.steam_id,
                                  func.coalesce(sq2.c.wr_count, '0').label('wr_count'),
                                  sq3.c.record_count.label('record_count')).\
        outerjoin(sq2, sq2.c.id == Player.id).\
        join(sq3, sq3.c.id == Player.id).\
        order_by(Player.name).\
        paginate(page, ROWS_PER_PAGE, True)
    return render_template('players.html',
                           title='Players',
                           pagination=pagination)


@root.route('/records/', defaults={'page': 1})
@root.route('/records/page/<int:page>')
def records(page):
    pagination = db.session.query(Record.mode,
                                  Record.time,
                                  Record.date,
                                  Player.name.label('player_name'),
                                  Map.name.label('map_name'),
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Player, Map).\
        order_by(desc(Record.date)).\
        paginate(page, ROWS_PER_PAGE, True)
    return render_template('records.html',
                           title='Records',
                           pagination=pagination)


@root.route('/maps/')
def maps():
    return render_template('maps.html')


@root.route('/api/')
def api():
    pass


@root.before_app_request
def before_request():
    # Save current time. Used to time request duration.
    g.start_time = time()


@root.after_app_request
def after_request(response):
    """ Replace the string __EXECUTION_TIME__ in the response with the execution time."""
    session['previous_page'] = request.url
    execution_time = round((time() - g.start_time) * 1000)
    execution_time_string = '1 millisecond' if execution_time == 1 else f'{execution_time} milliseconds'
    if response.response:
        try:
            response.response[0] = response.response[0].replace('__EXECUTION_TIME__'.encode('utf-8'), execution_time_string.encode('utf-8'))
            response.headers['content-length'] = len(response.response[0])
        except TypeError:
            # Response does not contain the string __EXECUTION_TIME__
            pass
    return response


def setup_error_routing(app):
    @app.errorhandler(404)
    def not_found_error(error):
        try:
            redirect_url = session['previous_page']
        except KeyError:
            redirect_url = url_for('root.index')
        return render_template('404.html', title='404', redirect_url=redirect_url), 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            redirect_url = session['previous_page']
        except KeyError:
            redirect_url = url_for('root.index')
        return render_template('500.html', title='500', redirect_url=redirect_url), 500
