from typing import List, Optional

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(buttons: List[List[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)


def get_inline_button(
        button_str: Optional[str] = None,
        callback_data: Optional[str] = None,
        url: Optional[str] = None
) -> InlineKeyboardButton:
    return InlineKeyboardButton(button_str, callback_data=callback_data, url=url)


def get_inline_keyboard(
        buttons: List[List[InlineKeyboardButton]]
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(buttons)
