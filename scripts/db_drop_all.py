"""Drops all database tables, use with caution"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app

response = ''
while response.lower() not in ('y', 'n'):
    response = input('Are you sure you want to drop all database tables? y/n\n')
if response.lower() == 'y':
    app = create_app('config.scripts_config')
    with app.app_context():
        db.reflect()
        db.drop_all()
        db.session.commit()
