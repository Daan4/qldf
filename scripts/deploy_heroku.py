"""
First time setup of environment variables and postgres addon when deploying on Heroku
Run with
heroku run python scripts/deploy_heroku.py
"""
import os
import subprocess

# Set heroku config variables
os.environ['QLDF_CONFIG'] = 'config.heroku_config'
os.environ['SECRET_KEY'] = 'ENTER THE SECRET KEY HERE SOMEHOW'
os.environ['PORT'] = '5000'
# Create database with test data
subprocess.call('python scripts/db_create.py')
subprocess.call('python scripts/db_populate.py')
# Init database migrations
subprocess.call(['python', 'scripts/db_manage.py', 'db', 'init'])
