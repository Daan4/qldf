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

2. Create config/website_config.py and add the following contents:
```
SECRET_KEY = 'your super secret key goes here'

# Database settings
DB_USERNAME = 'postgres'
DB_PASSWORD = 'password'
DB_HOST = 'localhost'
DB_NAME = 'qldf'
DB_PORT = 5433  # usually 5432 or 5433
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(DB_USERNAME,
                                                            DB_PASSWORD,
                                                            DB_HOST,
                                                            DB_NAME)

# Mail settings
MAIL_HOST = "localhost"
MAIL_PORT = "25"
MAIL_USERNAME = None
MAIL_PASSWORD = None

# Admin emails
ADMINS = ['admin@example.com']
```

2. Download and install postgres v10.1+, then create the qldf database.

Run from "..\PostgreSQL\10\bin":
```
createdb -U postgres -T template0 -E utf-8 -l american_usa qldf
```

3. Create database tables.

Run from \scripts in the virtualenv:
```
db_create
```

4. Setup database migration directory.

Run from \scripts in the virtualenv:
```
db_manage db init
```

# Generate requirements.txt
Run from virtualenv:
```
pip freeze > requirements.txt
```

# Update the database
Whenever changes are made to database models in any models.py file run the following to update the database.

Run from \scripts in the virtualenv:
```
db_manage db migrate
db_manage db upgrade
```

To revert changes:
```
db_manage db downgrade
```

# Deploying on Heroku
Follow these instructions:
https://devcenter.heroku.com/articles/getting-started-with-python#introduction
