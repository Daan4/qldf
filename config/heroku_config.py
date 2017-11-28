import os
import config.config as c

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask settings
DEBUG = True
USE_RELOADER = False
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))

# Flask-SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_MIGRATE_REPO = c.SQLALCHEMY_MIGRATE_REPO
SQLALCHEMY_TRACK_MODIFICATIONS = c.SQLALCHEMY_TRACK_MODIFICATIONS

# Mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 1234
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'

# Administrator list
ADMINS = ['Daan@example.com']

# Super secret key
SECRET_KEY = os.environ.get('SECRET_KEY')

# Pagination settings
ROWS_PER_PAGE = 20
SEARCH_RESULTS_PER_PAGE = c.SEARCH_RESULTS_PER_PAGE

# Number of rows to show on the index page recent tables
NUM_RECENT_RECORDS = c.NUM_RECENT_RECORDS
NUM_RECENT_MAPS = c.NUM_RECENT_MAPS
NUM_RECENT_WORLD_RECORDS = c.NUM_RECENT_WORLD_RECORDS

# Steam base URLs
# Append the workshop item id
STEAMWORKSHOP_ITEM_URL = c.STEAMWORKSHOP_ITEM_URL
# Append player steamID64
STEAMPLAYER_PROFILE_URL = c.STEAMPLAYER_PROFILE_URL

# Limits the # of maps the database gets populated with
MAP_LIMIT = 20

# Record physics modes
RECORD_MODES = c.RECORD_MODES

# syncore api urls
SYNCORE_SERVERS_URL = c.SYNCORE_SERVERS_URL

# APScheduler tasks
SCHEDULER_API_ENABLED = c.SCHEDULER_API_ENABLED
JOBS = c.JOBS

# Logging
LOG_INFO_FILENAME = c.LOG_INFO_FILENAME
LOG_DEBUG_FILENAME = c.LOG_DEBUG_FILENAME
