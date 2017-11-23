from flask import Blueprint, render_template, session, url_for, g, request
from time import time
from .models import Player, Record, Map
from config.config import ROWS_PER_PAGE
from sqlalchemy import func, and_
from qldf import db

root = Blueprint('root', __name__, url_prefix='')


@root.route('/')
def index():
    return render_template('index.html')


@root.route('/servers/')
def servers():
    return render_template('servers.html')


@root.route('/players/', defaults={'page': 1})
@root.route('/players/page/<int:page>')
def players(page):
    # see https://stackoverflow.com/questions/6206600/sqlalchemy-subquery-in-a-where-clause
    # t = db.session.query(Player.id,
    #                      func.count(Player.id).label('record_count'),
    # ).join(Player.records).group_by(Player.id).subquery('t')
    # pagination = db.session.query(Player, Record).filter(and_(
    #     Player.id == Record.player_id,
    #     Player.id == t.c.id
    # )).order_by(Player.name).paginate(page, ROWS_PER_PAGE, True)
    # pagination = db.session.query(Player).\
    #     outerjoin(Player.records).\
    #     filter(Player.id == Record.player_id). \
    #     add_column(func.count(Player.id)). \
    #     group_by(Player.id).\
    #     paginate(page, ROWS_PER_PAGE, True)\
    #https://stackoverflow.com/questions/41362153/sqlalchemy-count-function-for-nested-join-subquery
    stmt = db.session.query(
        Player.id,
        func.count(Record.player_id.distinct()).label('record_count')
    ).join(Record).\
        group_by(Player.id).\
        subquery()

    print(str(db.session.query(Player,
                                  stmt.c.record_count).\
        outerjoin(stmt, Player.id == stmt.c.id).\
        order_by(Player.name).paginate(page, ROWS_PER_PAGE,True))


    return render_template('players.html',
                           title='Players',
                           pagination=pagination)


@root.route('/records/')
def records():
    return render_template('records.html')


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
