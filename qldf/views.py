from flask import Blueprint, render_template, session, url_for, g, request, current_app
from time import time
from .models import Player, Record, Map
from sqlalchemy import func, desc, asc
from qldf import db

root = Blueprint('root', __name__, url_prefix='/')


@root.route('/')
def index():
    return render_template('index.html')


@root.route('servers/')
def servers():
    return render_template('servers.html')


@root.route('player/<string:name>/', defaults={'page': 1, 'sortby': 'date', 'sortdir': desc})
@root.route('player/<string:name>/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('player/<string:name>/<int:page>/<string:sortby>/', defaults={'sortdir': desc})
@root.route('player/<string:name>/<int:page>/', defaults={'sortby': 'date', 'sortdir': desc})
def player(page, name, sortby, sortdir):
    """Show records and stats for a single player"""
    if sortdir == 'asc':
        sortdir = asc
    else:
        sortdir = desc
    # Get 'rank' in subquery before filtering on player name and ordering
    sq = db.session.query(Record.mode.label('mode'),
                          Record.time.label('time'),
                          Record.date.label('date'),
                          Record.player_id.label('player_id'),
                          Map.name.label('map_name'),
                          func.rank().over(
                              order_by=Record.time,
                              partition_by=(Record.map_id, Record.mode)
                          ).label('rank')).\
        join(Map).\
        subquery()
    pagination = db.session.query(Player.id,
                                  sq.c.mode.label('mode'),
                                  sq.c.time.label('time'),
                                  sq.c.date.label('date'),
                                  sq.c.map_name.label('map_name'),
                                  sq.c.rank.label('rank')).\
        join(sq, sq.c.player_id == Player.id).\
        filter(Player.name == name).\
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('player.html',
                           title=name,
                           name=name,
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


@root.route('players/', defaults={'page': 1})
@root.route('players/<int:page>/')
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
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('players.html',
                           title='Players',
                           pagination=pagination)


@root.route('records/', defaults={'page': 1})
@root.route('records/<int:page>/')
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
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('records.html',
                           title='Records',
                           pagination=pagination)


@root.route('map/<string:name>/', defaults={'page': 1})
@root.route('map/<string:name>/<int:page>/')
def _map(page, name):
    """Show records on a single map."""
    pagination = db.session.query(Record.mode,
                                  Record.time,
                                  Record.date,
                                  Player.name.label('player_name'),
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Map, Player).\
        filter(Map.name == name).\
        order_by(desc(Record.date)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('map.html',
                           title=name,
                           name=name,
                           pagination=pagination)


@root.route('maps/', defaults={'page': 1})
@root.route('maps/<int:page>/')
def maps(page):
    """Show a list of maps and the number of records on it"""
    pagination = db.session.query(Map.id,
                                  Map.name,
                                  func.count(Map.id).label('record_count')).\
        join(Map.records).\
        group_by(Map.id).\
        order_by(Map.name).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('maps.html',
                           title='Maps',
                           pagination=pagination)


@root.route('api/')
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
