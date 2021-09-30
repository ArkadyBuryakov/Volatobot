from kraken_bot import kraken_bot
from utils.telegram import send_telegram_message
from time import sleep
from orm import Base, engine
from logging.config import dictConfig
from settings import LOGGING


dictConfig(LOGGING)

# the easiest way to create tables
# but better to use https://alembic.sqlalchemy.org/
# so, it store migration story as well
Base.metadata.create_all(bind=engine)


def release_kraken():
    while True:
        kraken_bot()

        sleep(5)


if __name__ == '__main__':
    # Inform about starting
    # noinspection PyBroadException
    try:
        send_telegram_message('Successful start!')
    except Exception:
        pass

    # Start kraken_bot
    release_kraken()
