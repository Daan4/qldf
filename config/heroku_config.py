import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

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
SEARCH_RESULTS_PER_PAGE = 20

# Number of rows to show on the index page recent tables
NUM_RECENT_RECORDS = 25
NUM_RECENT_MAPS = 25
NUM_RECENT_WORLD_RECORDS = 25

# Record physics modes
RECORD_MODES = ['PQL Weapons',
                'PQL Strafe',
                'VQL Weapons',
                'VQL Strafe',
                'VQ3',
                'CPM']
