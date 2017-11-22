import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from qldf import db, create_app

app = create_app('config.config')
with app.app_context():
    db.create_all()
