from kraken_bot import kraken_bot
from time import sleep


def release_kraken():
    while True:
        kraken_bot()

        sleep(5)


if __name__ == '__main__':
    release_kraken()
