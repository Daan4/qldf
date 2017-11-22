from qldf import db, create_app

create_app('config.config')
db.create_all()
