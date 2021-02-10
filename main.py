from kraken_bot import kraken_bot
from telegram_manager import send_telegram_message
from time import sleep


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
