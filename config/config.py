import os
from config import website_config as c

basedir = os.path.abspath(os.path.dirname(__file__))

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
