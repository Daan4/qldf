import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail server settings
MAIL_SERVER = None
MAIL_PORT = None
MAIL_USERNAME = None
MAIL_PASSWORD = None

# Administrator list
ADMINS = []

# Super secret key
SECRET_KEY = os.environ.get('SECRET_KEY')

# Pagination settings
ROWS_PER_PAGE = 20

# Record physics modes
RECORD_MODES = ['PQL Weapons',
                'PQL Strafe',
                'VQL Weapons',
                'VQL Strafe',
                'VQ3',
                'CPM']
