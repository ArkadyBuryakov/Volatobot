import telegram
from settings import telegram_api_key
from settings import telegram_chat_id


telegram_bot = telegram.Bot(telegram_api_key)


def send_telegram_message(text):
    telegram_bot.send_message(telegram_chat_id, text)
    pass
