from bot.handlers import setup_dispatcher
from telegram.ext import Updater, PicklePersistence


def start_bot(token: str) -> None:
    updater = Updater(token, persistence=PicklePersistence('conv_data'))
    setup_dispatcher(updater)
    updater.start_polling()
    updater.idle()
