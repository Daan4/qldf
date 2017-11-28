"""Deleted all rows from all tables, use with caution"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app

response = ''
while response.lower() not in ('y', 'n'):
    response = input('Are you sure you want to delete all table rows? y/n\n')
if response.lower() == 'y':
    app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'))
    with app.app_context():
        from qldf.models import Map, Player, Record, WorkshopItem

        Record.query.delete()
        Player.query.delete()
        Map.query.delete()
        WorkshopItem.query.delete()
        db.session.commit()
