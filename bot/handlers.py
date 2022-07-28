import os
import uuid
from os.path import exists

from pyqiwip2p import QiwiP2P
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

import bot.localization as lc
from bot.config import QIWI_P2P, logger, ADMINS
from bot.decorators import admin_command, enrich_response_data
from bot.keyboards import MENU_KB, ADMIN_MENU_KB
from bot.utils import get_inline_keyboard, get_inline_button, get_active_users, parse_log

START, MENU, RETURN, REVOKE = range(4)
END = ConversationHandler.END


@enrich_response_data(
    text=(lc.VPN_START_MSG, lc.VPN_START_MSG + '\n\nAdmin Access'),
    inline_kb=(MENU_KB, ADMIN_MENU_KB)
)
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    text = context.chat_data['text']
    kb = context.chat_data['inline_kb']
    if hasattr(update.message, 'reply_text'):
        update.message.reply_text(text.format(user.first_name), reply_markup=kb)
    else:
        update.callback_query.edit_message_text(text.format(user.first_name), reply_markup=kb)
    return MENU


@admin_command
def echo_users(update: Update, context: CallbackContext) -> None:
    context.chat_data['message'] = update.message.text
    update.message.reply_text(
        update.message.text,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.YES, 'send')],
                [get_inline_button(lc.NO, '!send')]
            ]
        )
    )


@admin_command
def send_messages(update: Update, context: CallbackContext) -> None:
    if update.callback_query.data == 'send':
        user_ids = get_active_users()
        for uid in user_ids:
            context.bot.send_message(uid, context.chat_data['message'])
    update.callback_query.delete_message()


def app_info(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=lc.APP_INFO,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.IOS_LINK[0], url=lc.IOS_LINK[1])],
                [get_inline_button(lc.ANDROID_LINK[0], url=lc.ANDROID_LINK[1])],
                [get_inline_button(lc.WIN_LINK[0], url=lc.WIN_LINK[1])],
                [get_inline_button(lc.MACOS_LINK[0], url=lc.MACOS_LINK[1])],
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )
    return RETURN


def generate_cert(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    update.callback_query.edit_message_text(
        lc.GUIDE.format(user.first_name),
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )

    if not exists(f'bot/static_certificates/{user.id}.ovpn'):
        os.system(f'bash bot/bash_scripts/createuser.sh {user.id} &>> bot/log/rsa-gen.log')
        logger.info(f'Added new user: {user.full_name}, {user.id}')
    try:
        cert = open(f'bot/static_certificates/{user.id}.ovpn', 'rb')
        context.bot.send_document(
            chat_id=user.id,
            document=cert,
            filename=str(user.first_name) + '.ovpn'
        )
    except FileNotFoundError:
        update.callback_query.edit_message_text(
            'Конфиг не сгенерировался, пиши мне в лс @vadimkh7',
            reply_markup=get_inline_keyboard(
                [
                    [get_inline_button(lc.BACK, 'back')]
                ]
            )
        )

    return RETURN


def revoke_cert(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if not exists(f'bot/static_certificates/{user.id}.ovpn'):
        update.callback_query.edit_message_text(
            lc.CERT_NOT_GENERATED,
            reply_markup=get_inline_keyboard(
                [
                    [get_inline_button(lc.BACK, 'back')]
                ]
            )
        )
        return RETURN
    update.callback_query.edit_message_text(
        lc.CERT_PURGING_YN,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.YES, 'purge')],
                [get_inline_button(lc.NO, 'back')]
            ]
        )
    )
    return REVOKE


def purge_cert(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    os.system(f'bot/static_certificates/{user.id}.ovpn')
    os.system(f'bash bot/bash_scripts/revokeuser.sh {user.id} &>> bot/log/rsa-revoke.log')

    update.callback_query.edit_message_text(
        lc.CERT_PURGED,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )
    return RETURN


def get_beer_money(update: Update, context: CallbackContext) -> int:
    p2p = QiwiP2P(auth_key=QIWI_P2P)
    comment = str(uuid.uuid4()) + ' ' + update.effective_user.full_name
    bill = p2p.bill(amount=150, lifetime=60*24, comment=comment)
    update.callback_query.edit_message_text(
        lc.THANK_YOU,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.QIWI_BTN, url=bill.pay_url)],
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )
    return RETURN


@admin_command
def get_users(update: Update, context: CallbackContext) -> int:
    status_log = parse_log(str(open('/var/log/openvpn/openvpn-status.log').read()))
    text = 'List of all users:\n'
    for i, uid in enumerate(get_active_users(), 1):
        chat = context.bot.getChat(uid)
        status = '🟢' if str(uid) in status_log else '🔴'
        if hasattr(chat, 'username'):
            try:
                text += f'{i}. {chat.first_name} {chat.last_name} @{chat.username} - {uid}{status}\n'
            except AttributeError:
                text = f'{i}. @{chat.username} - {uid}{status}\n'
        else:
            text += f'UNDEF: {uid}'
    update.callback_query.edit_message_text(
        text,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )
    return RETURN


def get_stats(update: Update, context: CallbackContext) -> int:
    status_log = parse_log(str(open('/var/log/openvpn/openvpn-status.log').read()))
    text = f'Пользуются VPN прямо сейчас: {len(status_log)}\n'
    if str(update.effective_user.id) in ADMINS:
        for i, (name, log) in enumerate(status_log.items(), 1):
            try:
                int(name)
                valid_name = context.bot.getChat(name).username
                text += f'{i}. @{valid_name}\n'
            except ValueError:
                valid_name = name
                text += f'{i}. {valid_name}\n'
    update.callback_query.edit_message_text(
        text,
        reply_markup=get_inline_keyboard(
            [
                [get_inline_button(lc.BACK, 'back')]
            ]
        )
    )
    return RETURN


def setup_dispatcher(updater: Updater) -> None:
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(app_info, pattern='app'),
                CallbackQueryHandler(generate_cert, pattern='key'),
                CallbackQueryHandler(revoke_cert, pattern='revoke'),
                CallbackQueryHandler(get_beer_money, pattern='pay'),
                CallbackQueryHandler(get_users, pattern='users'),
                CallbackQueryHandler(get_stats, pattern='stats'),
            ],
            RETURN: [CallbackQueryHandler(start, pattern='back')],
            REVOKE: [
                CallbackQueryHandler(purge_cert, pattern='purge'),
                CallbackQueryHandler(start, pattern='back')
            ]
        },
        fallbacks=[],
        persistent=True,
        name='conv',
        allow_reentry=True
    )
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_users))
    dispatcher.add_handler(CallbackQueryHandler(send_messages, pattern='send'))
    dispatcher.add_handler(CallbackQueryHandler(send_messages, pattern='!send'))
    dispatcher.add_handler(conv_handler)
