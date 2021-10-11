import telegram
from settings import TELEGRAM_BOT_TOKEN
from settings import TELEGRAM_CHAT_ID


telegram_bot = telegram.Bot(TELEGRAM_BOT_TOKEN)


def send_telegram_message(text, parse_mode=None):
    telegram_bot.send_message(TELEGRAM_CHAT_ID, text, parse_mode=parse_mode)
    pass
