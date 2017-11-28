import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app

app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'))
with app.app_context():
    db.create_all()
    db.session.commit()
