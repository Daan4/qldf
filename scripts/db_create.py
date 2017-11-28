import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app

app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'), create_logfiles=False)
with app.app_context():
    from qldf.root.models import Map, Player, Record, Server
    db.create_all()
    db.session.commit()
