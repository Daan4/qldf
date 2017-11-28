import os

from flask_apscheduler import APScheduler
from flask_navigation import Navigation
from flask_sqlalchemy import SQLAlchemy

from qldf.root.filters import setup_custom_jinja_filters

db = SQLAlchemy()
nav = Navigation()


def create_app(config):
    """Create and initialise the object"""
    # Flask
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(config)
    # SQLAlchemy
    db.init_app(app)
    db.app = app
    # Setup navigation
    setup_navigation(app)
    # Run tasks on startup if needed
    if app.config['RUN_TASKS_ON_STARTUP']:
        from qldf.tasks import update_servers, update_players, update_workshop_items
        update_players()
        #update_workshop_items()
        #update_servers()
    # Setup and start apscheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    # Register blueprints
    from .root.views import root, setup_error_routing
    from .api.views import api
    app.register_blueprint(api)
    app.register_blueprint(root)
    # Setup routing for html error pages
    setup_error_routing(app)
    # Setup logging
    setup_logging(app)
    # Setup custom jinja filters
    setup_custom_jinja_filters(app)
    return app


def setup_navigation(app):
    # Flask-Navigation setup
    nav.init_app(app)
    # Add navigation bar items
    items = [nav.Item('Home', 'root.index'),
             nav.Item('Records', 'root.records'),
             nav.Item('Maps', 'root.maps'),
             nav.Item('Players', 'root.players'),
             nav.Item('Servers', 'root.servers')]
    nav.Bar('main', items)


def setup_logging(app):
    import logging
    from logging.handlers import RotatingFileHandler
    # Log via files
    # INFO or higher
    logfolder = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(os.path.dirname(logfolder)):
        os.mkdir(logfolder)
    file_handler = RotatingFileHandler(os.path.join(logfolder, app.config['LOG_INFO_FILENAME']), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s in %(pathname)s:%(lineno)d'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
