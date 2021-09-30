"""
Global settings for script and environment variables.

All settings from database should be fetched using get_setting() from ORM.py
"""
from os import getenv


DEBUG = int(getenv("DEBUG", 0))

# Load environment variables from .env file
# In productive set variables manually or by secrets manager
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()

# Get environment variables
DATABASE_URL = getenv("DATABASE_URL") or (
    getenv("DATABASE_ENGINE", 'postgres') + "://" +
    getenv("DATABASE_USER", 'foo') + ":" +
    getenv("DATABASE_PASSWORD", 'foo') + "@" +
    getenv("DATABASE_HOST", 'localhost') + ":" +
    getenv("DATABASE_PORT", '5432') + "/" +
    getenv("DATABASE_NAME", 'volatabot_dev')
)
KRAKEN_KEY = getenv("KRAKEN_KEY")
KRAKEN_PRIVATE_KEY = getenv("KRAKEN_PRIVATE_KEY")
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
             'datefmt': '%y %b %d, %H:%M:%S',
            },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        'telegram': {
            'class': 'utils.logging.TelegramHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'] if DEBUG else ['console', 'telegram'],
        'level': 'INFO',
    },
}
