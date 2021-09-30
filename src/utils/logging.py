"""Kinda repeat of https://gist.github.com/AlcibiadesCleinias/0bcdcb8347201d78c4d05339df0dcc82"""

import logging
from datetime import datetime
from utils.telegram import send_telegram_message


class EMOJI:
    WHITE_CIRCLE = '\U000026AA'
    BLUE_CIRCLE = '\U0001F535'
    RED_CIRCLE = '\U0001F534'


class TelegramFormatter(logging.Formatter):
    """Works not as expected since there may be different python version !todo
    with different logging.Formatter base class =(
    """
    fmt = '<code>%(asctime)s</code> <b>%(levelname)s</b>\nFrom %(name)s:%(funcName)s\n%(message)s'
    parse_mode = 'HTML'

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)

    @staticmethod
    def escape_html(text):
        """
        Escapes all html characters in text
        :param str text:
        :rtype: str
        """
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    @staticmethod
    def compose_levelname_with_emoji(record):
        if record.levelno == logging.DEBUG:
            record.levelname += ' ' + EMOJI.WHITE_CIRCLE
        elif record.levelno == logging.INFO:
            record.levelname += ' ' + EMOJI.BLUE_CIRCLE
        else:
            record.levelname += ' ' + EMOJI.RED_CIRCLE
        return record.levelname

    def format(self, record):
        """
        :param logging.LogRecord record:
        """
        if record.funcName:
            record.funcName = self.escape_html(str(record.funcName))
        if record.name:
            record.name = self.escape_html(str(record.name))
        if record.msg:
            record.msg = self.escape_html(record.getMessage())
        if record.exc_text:
            record.exc_text = '<code>' + self.escape_html(record.exc_text) + '</code>'

        record.levelname = TelegramFormatter.compose_levelname_with_emoji(record)

        try:
            return super().format(record=record)
        except TypeError:  # coz of different pythons
            super(TelegramFormatter, self).format(record)
            return self.fmt % record.__dict__


class TelegramHandler(logging.StreamHandler):
    """Works perfect without formatter with different python logging versions."""

    def _compose_msg_with_header(self, record):  # todo: make optional
        msg = self.format(record)
        levelname_with_emoji = TelegramFormatter.compose_levelname_with_emoji(record)

        return (
            f"`{datetime.fromtimestamp(record.created)}` *{levelname_with_emoji}*\n"
            f"```\n{msg}\n```"
        )

    def emit(self, record):
        msg = self._compose_msg_with_header(record=record)

        parse_mode = 'Markdown'
        if getattr(self.formatter, 'parse_mode', None):
            parse_mode = self.formatter.parse_mode

        send_telegram_message(text=msg, parse_mode=parse_mode)
