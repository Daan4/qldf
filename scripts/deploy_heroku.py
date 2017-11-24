"""
First time setup of environment variables and postgres addon when deploying on Heroku
Run with

"""
import os
import subprocess

# Set heroku config variables
os.environ['QLDF_CONFIG'] = 'config.heroku_config'
os.environ['SECRET_KEY'] = 'ENTER THE SECRET KEY HERE SOMEHOW'
os.environ['PORT'] = '5000'
# Create database with test data
subprocess.call('scripts/db_create.py')
subprocess.call('scripts/db_populate.py')
# Init database migrations
subprocess.call(['scripts/db_manage.py', 'db', 'init'])
