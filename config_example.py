"""API backend configuration file."""

import os
import urllib.parse

# Base project directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# CDN server address
CDN_ADDRESS = 'http://cdn.gaspiko.lc/files'

# URL's to directories on CDN server
CDN_AVATARS_FOLDER = urllib.parse.urljoin(CDN_ADDRESS, 'users/')

# Database connection
DB_USER = "..."
DB_PSWD = "..."
SQLALCHEMY_BASIC_URI = 'mysql+pymysql://%s:%s@localhost/' % (DB_USER, DB_PSWD)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@localhost/' \
    'innerInformationSystem_System' % (DB_USER, DB_PSWD)
SQLALCHEMY_BINDS = {
    # 'kartoteka': 'mysql+pymysql://goomba:tester@localhost/kartoteka',
    'inventory': 'mysql+pymysql://%s:%s@localhost/'
    'innerInformationSystem_Inventory' % (DB_USER, DB_PSWD)
}
SQLALCHEMY_TRACK_MODIFICATIONS = 'true'

# Default settings
LIMIT = 20  # Number of records in paginated json
USER_MAIL_RENEW = 20  # Time (in days) after which need to confirm mail
USER_PASSWORD_RENEW = 20  # Time (in days) after which need to renew password
JSON_AS_ASCII = False  # Turn off encoding json as ASCII default

# Authentification settings
SECRET_KEY = "..."  # Secret key
TOKEN_DURATION = 1  # Time (in days) of authentication token validity

# Mail check and verification
# VERIFICATION_SALT = "..."  # Salt for link generation

# Mail client for sending mails to users
# MAIL_SERVER = 'smtp.yandex.ru'
# MAIL_PORT = 465

# MAIL_USE_TLS = False
# MAIL_USE_SSL = True

# MAIL_USERNAME = '...'
# MAIL_PASSWORD = '...'
# MAIL_DEFAULT_SENDER = "..."
