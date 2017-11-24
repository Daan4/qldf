SECRET_KEY = 'super secret key'  # change this

# Database settings
DB_USERNAME = 'username'  # change this
DB_PASSWORD = 'password'  # change this
DB_HOST = 'localhost'  # change this
DB_NAME = 'qldf'
DB_PORT = 5432  # change this, usually 5432 or 5433
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(DB_USERNAME,
                                                            DB_PASSWORD,
                                                            DB_HOST,
                                                            DB_NAME)

# Mail settings
MAIL_HOST = "localhost"  # change this if working with email
MAIL_PORT = "25"  # change this if working with email
MAIL_USERNAME = None  # change this, keep either username or password as None to not use logging via mail
MAIL_PASSWORD = None  # change this, keep either username or password as None to not use logging via mail

# Admin emails
ADMINS = ['admin@example.com']  # change this if working with email
