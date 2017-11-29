import os
from config import local_config as c

basedir = os.path.abspath(os.path.dirname(__file__))


# Flask settings
DEBUG = True
USE_RELOADER = False
HOST = None  # Defaults
PORT = None  # Defaults

# Flask-SQLAlchemy settings
DB_USERNAME = c.DB_USERNAME
DB_PASSWORD = c.DB_PASSWORD
DB_HOST = c.DB_HOST
DB_NAME = c.DB_NAME
DB_PORT = c.DB_PORT
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail server settings
MAIL_SERVER = c.MAIL_HOST
MAIL_PORT = c.MAIL_PORT
MAIL_USERNAME = c.MAIL_USERNAME
MAIL_PASSWORD = c.MAIL_PASSWORD

# Administrator list
ADMINS = c.ADMINS

# Super secret key
SECRET_KEY = c.SECRET_KEY

# Pagination settings
ROWS_PER_PAGE = 20
SEARCH_RESULTS_PER_PAGE = 20

# Number of rows to show on the index page recent tables
NUM_RECENT_RECORDS = 25
NUM_RECENT_MAPS = 25
NUM_RECENT_WORLD_RECORDS = 25

# Steam base URLs
# Append the workshop item id
STEAMWORKSHOP_ITEM_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id="
# Append player steamID64
STEAMPLAYER_PROFILE_URL = "https://steamcommunity.com/profiles/"
# Append search string
STEAMWORKSHOP_SEARCH_URL = 'https://steamcommunity.com/workshop/browse/?appid=282440&searchtext='

# Record physics modes
RECORD_MODES = ['PQL Weapons',
                'PQL Strafe',
                'VQL Weapons',
                'VQL Strafe',
                'VQ3',
                'CPM']

# syncore api urls
SYNCORE_SERVERS_URL = 'https://ql.syncore.org/api/servers'

# APScheduler tasks
RUN_TASKS_ON_STARTUP = c.RUN_TASKS_ON_STARTUP
SCHEDULER_API_ENABLED = True
JOBS = [
    {
        'id': 'update_servers',
        'func': 'qldf.tasks:update_servers',
        'trigger': 'interval',
        'seconds': c.UPDATE_SERVERS_INTERVAL
    },
    {
        'id': 'update_player',
        'func': 'qldf.tasks:update_players',
        'trigger': 'interval',
        'seconds': c.UPDATE_PLAYERS_INTERVAL
    },
    {
        'id': 'update_workshop_items',
        'func': 'qldf.tasks:update_workshop_items',
        'trigger': 'interval',
        'seconds': c.UPDATE_WORKSHOPITEMS_INTERVAL
    }
]

# Logging
LOG_INFO_FILENAME = 'qldf_info.log'
LOG_DEBUG_FILENAME = 'qldf_debug.log'
