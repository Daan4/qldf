import sys
import os
sys.path.insert(0, os.path.abspath('..'))
from qldf import db, create_app

app = create_app('config.config', create_logfiles=False)
with app.app_context():
    from qldf.models import Map, Player, Record
    db.create_all()
    db.session.commit()
