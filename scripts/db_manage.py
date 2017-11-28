import os
import sys

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qldf import db, create_app

# available commands
# db init : create migrations folder
# db migrate : create migration
# db upgrade [<revision>] : upgrade database to revision
# db downgrade [<revision>] : downgrade database to revision

app = create_app(os.environ.get('QLDF_CONFIG', 'config.config'))

# setup Flask-Migrate
migrate = Migrate(app, db, directory=os.path.abspath('migrations'))
manager = Manager(app)
manager.add_command('db', MigrateCommand)

manager.run()
