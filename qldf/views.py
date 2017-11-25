from flask import Blueprint, render_template, session, url_for, g, request, current_app
from time import time
from .models import Player, Record, Map
from .forms import SearchForm, SEARCH_TYPES
from sqlalchemy import func, desc, asc
from qldf import db

root = Blueprint('root', __name__, url_prefix='/', template_folder='templates', static_folder='static')


@root.route('/', methods=['GET', 'POST'])
def index():
    # Add search form
    search_form = SearchForm()
    if search_form.validate_on_submit() and search_form.search_data:
        # Do a search
        search_string = search_form.search_string.data
        search_type = search_form.search_type.data
        if search_type == SEARCH_TYPES[0]:
            search_results = db.session.query(Player.id,
                                              Player.name)
    # Get rows of recent records
    recent_records = db.session.query(Record.mode,
                                      Map.name.label('map_name'),
                                      Player.name.label('player_name'),
                                      Player.steam_id,
                                      Record.time,
                                      Record.date,
                                      func.rank().over(
                                          order_by=Record.time,
                                          partition_by=(Record.map_id, Record.mode)
                                      ).label('rank')).\
        join(Player, Map).\
        order_by(desc(Record.date)).\
        limit(current_app.config['NUM_RECENT_RECORDS'])

    # Get rows of recent world records
    sq = db.session.query(Record.id,
                          func.rank().over(
                              order_by=Record.time,
                              partition_by=(Record.map_id, Record.mode)
                          ).label('rank')).subquery()
    recent_world_records = db.session.query(Record.mode,
                                            Map.name.label('map_name'),
                                            Player.name.label('player_name'),
                                            Player.steam_id,
                                            Record.time,
                                            Record.date,
                                            sq.c.rank.label('rank')).\
        join(Player, Map).\
        join(sq, sq.c.id == Record.id).\
        filter(sq.c.rank == 1).\
        order_by(desc(Record.date)).\
        limit(current_app.config['NUM_RECENT_WORLD_RECORDS'])
    # Get rows of recent maps
    recent_maps = db.session.query(Map.name,
                                   Map.date_created).\
        order_by(desc(Map.date_created)).\
        limit(current_app.config['NUM_RECENT_MAPS'])
    return render_template('index.html',
                           recent_records=recent_records,
                           recent_world_records=recent_world_records,
                           recent_maps=recent_maps,
                           search_form=search_form)


@root.route('servers/')
def servers():
    return render_template('servers.html')


@root.route('player/<string:steam_id>/', defaults={'page': 1, 'sortby': 'date', 'sortdir': 'desc'})
@root.route('player/<string:steam_id>/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('player/<string:steam_id>/<int:page>/<string:sortby>/', defaults={'sortdir': 'asc'})
@root.route('player/<string:steam_id>/<int:page>/', defaults={'sortby': 'date', 'sortdir': 'desc'})
def player(page, steam_id, sortby, sortdir):
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
                                  Player.steam_id,
                                  Player.name.label('player_name'),
                                  sq.c.mode.label('mode'),
                                  sq.c.time.label('time'),
                                  sq.c.date.label('date'),
                                  sq.c.map_name.label('map_name'),
                                  sq.c.rank.label('rank')).\
        join(sq, sq.c.player_id == Player.id).\
        filter(Player.steam_id == steam_id).\
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    name = pagination.items[0].player_name
    return render_template('player.html',
                           title=steam_id,
                           name=name,
                           steam_id=steam_id,
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


@root.route('players/', defaults={'page': 1, 'sortby': 'name', 'sortdir': 'asc'})
@root.route('players/<int:page>/', defaults={'sortby': 'name', 'sortdir': 'asc'})
@root.route('players/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('players/<int:page>/<string:sortby>/', defaults={'sortdir': 'asc'})
def players(page, sortby, sortdir):
    """Show a list of all players and their number of records and world records."""
    if sortdir == 'asc':
        sortdir = asc
    else:
        sortdir = desc
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
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('players.html',
                           title='Players',
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


@root.route('records/', defaults={'page': 1, 'sortby': 'date', 'sortdir': 'desc'})
@root.route('records/<int:page>/', defaults={'sortby': 'date', 'sortdir': 'desc'})
@root.route('records/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('records/<int:page>/<string:sortby>/', defaults={'sortdir': 'asc'})
def records(page, sortby, sortdir):
    if sortdir == 'asc':
        sortdir = asc
    else:
        sortdir = desc
    pagination = db.session.query(Record.mode,
                                  Record.time,
                                  Record.date,
                                  Player.name.label('player_name'),
                                  Player.steam_id,
                                  Map.name.label('map_name'),
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Player, Map).\
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('records.html',
                           title='Records',
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


@root.route('map/<string:name>/', defaults={'page': 1, 'sortby': 'rank', 'sortdir': 'asc'})
@root.route('map/<string:name>/<int:page>/', defaults={'sortby': 'rank', 'sortdir': 'asc'})
@root.route('map/<string:name>/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('map/<string:name>/<int:page>/<string:sortby>/', defaults={'sortdir': 'asc'})
def _map(page, name, sortby, sortdir):
    """Show records on a single map."""
    if sortdir == 'asc':
        sortdir = asc
    else:
        sortdir = desc
    pagination = db.session.query(Record.mode,
                                  Record.time,
                                  Record.date,
                                  Player.name.label('player_name'),
                                  Player.steam_id,
                                  func.rank().over(
                                      order_by=Record.time,
                                      partition_by=(Record.map_id, Record.mode)
                                  ).label('rank')).\
        join(Map, Player).\
        filter(Map.name == name).\
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('map.html',
                           title=name,
                           name=name,
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


@root.route('maps/', defaults={'page': 1, 'sortby': 'name', 'sortdir': 'asc'})
@root.route('maps/<int:page>/', defaults={'sortby': 'name', 'sortdir': 'asc'})
@root.route('maps/<int:page>/<string:sortby>/<string:sortdir>/')
@root.route('maps/<int:page>/<string:sortby>/', defaults={'sortdir': 'asc'})
def maps(page, sortby, sortdir):
    if sortdir == 'asc':
        sortdir = asc
    else:
        sortdir = desc
    """Show a list of maps and the number of records on it"""
    pagination = db.session.query(Map.id,
                                  Map.name,
                                  func.count(Map.id).label('record_count')).\
        join(Map.records).\
        group_by(Map.id).\
        order_by(sortdir(sortby)).\
        paginate(page, current_app.config['ROWS_PER_PAGE'], True)
    return render_template('maps.html',
                           title='Maps',
                           pagination=pagination,
                           sortdir=sortdir.__name__,
                           reverse_sortdir_on=sortby)


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
