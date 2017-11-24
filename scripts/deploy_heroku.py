"""
First time setup of postgres db when deploying on Heroku
Run with
heroku run python scripts/deploy_heroku.py
"""
import subprocess

# Create database with test data
subprocess.call(['python', 'scripts/db_create.py'])
subprocess.call(['python', 'scripts/db_populate.py'])
# Init database migrations
subprocess.call(['python', 'scripts/db_manage.py', 'db', 'init'])
