"""Drops all database tables, use with caution"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from qldf import db, create_app

response = ''
while response.lower() not in ('y', 'n'):
    response = input('Are you sure you want to drop all database tables? y/n\n')
if response.lower() == 'y':
    app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)
    with app.app_context():
        from qldf.root.models import Map, Player, Record, WorkshopItem, Server
        db.reflect()
        db.drop_all()
        db.session.commit()
