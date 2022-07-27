import bot.localization as lc

from bot.utils import get_inline_keyboard, get_inline_button


MENU_KB = get_inline_keyboard(
    [
        [get_inline_button(lc.DOWNLOAD_APP, 'app')],
        [get_inline_button(lc.GENERATE_CERT, 'key')],
        [get_inline_button(lc.REVOKE_CERT, 'revoke')],
        [get_inline_button(lc.STATS, 'stats')],
        [get_inline_button(lc.DONATE_BTN, 'pay')],
    ]
)

ADMIN_MENU_KB = get_inline_keyboard(
    [
        [get_inline_button(lc.DOWNLOAD_APP, 'app')],
        [get_inline_button(lc.GENERATE_CERT, 'key')],
        [get_inline_button(lc.REVOKE_CERT, 'revoke')],
        [get_inline_button(lc.STATS, 'stats')],
        [get_inline_button(lc.USER_LIST, 'users')],
        [get_inline_button(lc.DONATE_BTN, 'pay')],
    ]
)