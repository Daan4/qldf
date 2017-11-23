import os
from config import website_config as c

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-SQLAlchemy settings
DB_USERNAME = c.DB_USERNAME
DB_PASSWORD = c.DB_PASSWORD
DB_HOST = c.DB_HOST
DB_NAME = c.DB_NAME
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail server settings
MAIL_SERVER = c.MAIL_HOST
MAIL_PORT = c.MAIL_PORT
MAIL_USERNAME = c.MAIL_USERNAME
MAIL_PASSWORD = c.MAIL_PASSWORD

# Administrator list
ADMINS = c.ADMINS