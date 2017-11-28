This readme file is a work in progress...

# Setup windows environment for development
1. Setup virtualenv (python version 3.6.3+) and install dependencies.

Run from project folder:
```
python -m pip install --user virtualenv
python -m virtualenv venv
venv\scripts\activate
pip install -r requirements.txt
```

2. Customize local_config_sample.py and rename it to local_config.py

3. Download and install postgres v10.x, then create the qldf database.

Run from "..\PostgreSQL\10\bin":
```
createdb -U postgres -T template0 -E utf-8 -l american_usa qldf
```

4. Create database tables and populate with test data.

Run from \scripts in the virtualenv:
```
python scripts\db_create.py
python scripts\db_populate.py

```

5. Setup database migration directory.

Run in the virtualenv:
```
python scripts\db_manage.py db init
```

# Generate requirements.txt
Run in the virtualenv:
```
pip freeze > requirements.txt
```

# Update the database schema
Whenever changes are made to database models in any models.py file run the following to update the database.

Run in the virtualenv:
```
python scripts\db_manage.py db migrate
python scripts\db_manage.py db upgrade
```

To revert changes:
```
python scripts\db_manage.py db downgrade
```

# Deploying on Heroku
Follow these instructions:
https://devcenter.heroku.com/articles/getting-started-with-python#introduction

Set the following config vars:
```
QLDF_CONFIG = config.heroku_config
PORT = 5000
SECRET_KEY = yoursupersecretkey
```

Create the database tables.

Other scripts can be ran in a similar way.
```
heroku run python scripts/deploy_heroku.py
```

Some other useful heroku cli commands
```
# Start web dyno
heroku ps:scale web=1
# Open page
heroku open
```
