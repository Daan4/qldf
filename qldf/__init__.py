from flask_sqlalchemy import SQLAlchemy
from config.config import *
from flask_navigation import Navigation

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
    # Flask-Navigation setup
    nav.init_app(app)
    # Add navigation bar items
    items = [nav.Item('Home', 'root.index'),
             nav.Item('Records', 'root.records'),
             nav.Item('Maps', 'root.maps'),
             nav.Item('Players', 'root.players'),
             nav.Item('Servers', 'root.servers')]
    nav.Bar('main', items)
    # Register blueprints
    from qldf.views import root, setup_error_routing
    app.register_blueprint(root)
    # Setup routing for html error pages
    setup_error_routing(app)
    # Setup logging
    import logging
    # Log via email
    if not app.debug:
        from logging.handlers import SMTPHandler
        credentials = None
        if MAIL_USERNAME and MAIL_PASSWORD:
            credentials = (MAIL_USERNAME, MAIL_PASSWORD)
        mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'www.qldf.com failure', credentials)
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
    file_handler = RotatingFileHandler('logs/website.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s in %(pathname)s:%(lineno)d'))
    app.logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    # DEBUG only
    file_handler = DebugRotatingFileHandler('logs/website_DEBUG.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.info('website startup')

    return app
