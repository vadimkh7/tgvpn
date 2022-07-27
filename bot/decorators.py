from typing import Tuple, Union, Any

from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from bot.config import ADMINS, DEBUG


def admin_command(func):
    def wrapper(update: Update, context: CallbackContext):
        user = update.effective_user
        if str(user.id) not in ADMINS:
            return
        return func(update, context)
    return wrapper


def enrich_response_data(
        text: Union[str, Tuple[str, str]] = None,
        inline_kb: Union[
            InlineKeyboardMarkup,
            Tuple[InlineKeyboardMarkup, InlineKeyboardMarkup]
        ] = None
):
    """
        Enriches response based on privileges.
    """
    def decorator(func):
        def wrapper(update: Update, context: CallbackContext):
            user = update.effective_user
            is_admin = str(user.id) in ADMINS
            text_tuple = (text, text) if isinstance(text, str) else text
            inline_kb_tuple = (inline_kb, inline_kb) if isinstance(inline_kb, InlineKeyboardMarkup) else inline_kb
            if text_tuple is not None:
                context.chat_data['text'] = text_tuple[is_admin]
            if inline_kb_tuple is not None:
                context.chat_data['inline_kb'] = inline_kb_tuple[is_admin]
            return func(update, context)
        return wrapper
    return decorator


def debug(return_val: Any):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if DEBUG:
                return return_val
            return func(*args, **kwargs)
        return wrapper
    return decorator

