This readme file is a work in progress...

# Setup windows environment for development
1. Setup virtualenv and install dependencies.

Run from project folder:
```
python -m pip install --user virtualenv
python -m virtualenv venv
venv\scripts\activate
pip install -r requirements.txt
```

2. Download and install postgres v10.1, then create the qldf database.

Run from "..\PostgreSQL\10\bin":
```
createdb -U postgres -T template0 -E utf-8 -l american_usa qldf
```

3. Create database tables.

Run from \scripts in the virtualenv:
```
db_create
```

4. Setup database migration.

Run from \scripts in the virtualenv:
```
db_manage db init
db_manage db migrate
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
