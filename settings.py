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
kraken_api_key = getenv("kraken_api_key")
kraken_private_api_key = getenv("kraken_private_api_key")
telegram_api_key = getenv("telegram_api_key")
telegram_chat_id = getenv("telegram_chat_id")
