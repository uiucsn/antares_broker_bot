from os import environ


ANTARES_API_KEY = environ.get('ANTARES_API_KEY', None)
ANTARES_API_SECRET = environ.get('ANTARES_API_SECRET', None)
TELEGRAM_API_TOKEN = environ.get('TELEGRAM_API_TOKEN', None)

SQL_HOSTNAME = 'antares_broker_bot_sql'
SQL_USERNAME = 'postgres'
SQL_DATABASE = 'antares_broker_bot'
