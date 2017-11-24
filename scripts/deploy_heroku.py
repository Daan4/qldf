"""
First time setup of environment variables and postgres addon when deploying on Heroku
Run with
heroku run python scripts/deploy_heroku.py
"""
import os
import subprocess

# Set heroku config variables
subprocess.call(['heroku', 'config:set', 'QLDF_CONFIG=config.heroku_config', 'SECRET_KEY=ENTERTHESECRETKEYHERESOMEHOW', 'PORT=5000'])
# Create database with test data
subprocess.call(['python', 'scripts/db_create.py'])
subprocess.call(['python', 'scripts/db_populate.py'])
# Init database migrations
subprocess.call(['python', 'scripts/db_manage.py', 'db', 'init'])
