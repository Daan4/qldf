"""Deleted all rows from all tables, use with caution"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from qldf import db, create_app

response = ''
while response.lower() not in ('y', 'n'):
    response = input('Are you sure you want to delete all table rows? y/n\n')
if response.lower() == 'y':
    app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)
    with app.app_context():
        from qldf.models import Map, Player, Record, WorkshopItem
        Map.query.delete()
        Player.query.delete()
        Record.query.delete()
        WorkshopItem.query.delete()
        db.session.commit()
