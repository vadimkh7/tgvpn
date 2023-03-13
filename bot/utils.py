import subprocess
from typing import List, Optional, Dict, Tuple, Union

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

from bot.config import ADMINS
from bot.decorators import debug


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


def get_active_users() -> List[str]:
    res = subprocess.run(
        ['bash', '/root/tgvpn/bot/bash_scripts/getusers.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    all_users = str(res.stdout).split('\n')
    telegram_users = []
    for u in all_users:
        try:
            int(u)
            telegram_users.append(u)
        except ValueError:
            continue
    return telegram_users


def parse_log(content: str) -> Dict[str, Dict[str, str]]:
    lines = content.split('\n')
    keywords = []
    for line in lines:
        if line.startswith('HEADER,CLIENT_LIST'):
            keywords = line.split(',')
            keywords.pop(0)
            keywords.pop(0)
            break
    users = []
    for line in lines:
        if line.startswith('CLIENT'):
            tmp = line.split(',')
            tmp.pop(0)
            if tmp[0] == 'UNDEF':
                continue
            users.append(tmp)
    parsed_log = {}
    for user in users:
        key = user[0]
        value = {}
        for i in range(len(keywords)):
            value[keywords[i]] = user[i]
        parsed_log[key] = value
    return parsed_log
