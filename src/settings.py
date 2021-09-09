"""
Global settings for script and environment variables.

All settings from database should be fetched using get_setting() from ORM.py
"""
from os import getenv


# Set debug mode (for application set False)
debug = True

# Load environment variables from .env file
# In productive set variables manually or by secrets manager
if debug:
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
