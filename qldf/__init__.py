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
    # Log via email
    if not app.debug:
        from logging.handlers import SMTPHandler
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        mail_handler = SMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']), 'no-reply@' + app.config['MAIL_SERVER'], app.config['ADMINS'], 'www.qldf.com failure', credentials)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    from logging.handlers import RotatingFileHandler

    class DebugRotatingFileHandler(RotatingFileHandler):
        def __init__(self, filename, mode='a', max_bytes=0, backup_count=0, encoding=None, delay=False):
            RotatingFileHandler.__init__(self, filename, mode, max_bytes, backup_count, encoding, delay)

        def emit(self, record):
            if record.levelno != logging.DEBUG:
                return
            RotatingFileHandler.emit(self, record)
    # Log via files
    # INFO or higher
    # Don't create logging directory and files when run from a different folder
    logfolder = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(os.path.dirname(logfolder)):
        os.mkdir(logfolder)
    file_handler = RotatingFileHandler(os.path.join(logfolder, app.config['LOG_INFO_FILENAME']), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s in %(pathname)s:%(lineno)d'))
    app.logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    # DEBUG only
    file_handler = DebugRotatingFileHandler(os.path.join(logfolder, app.config['LOG_DEBUG_FILENAME']), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
