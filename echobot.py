import datetime
import json
import logging
import os

from telegram import Update, ForceReply, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from buttons import actions_btns, firms_btns, timer_btns
from common import get_data, get_firm, Conf, Chat, pretty_day
from text_proc import filter_current_month, get_text_balance
from conf import TOKEN


def get_info(update: Update, context: CallbackContext, prompt: str = '👋 *Добро пожаловать.*\n\nВам доступна информация об этих аккаунтах:') -> None:
    if update.message:
        message = update.message
    else:
        message = update.callback_query.message

    try:
        username = message['chat']['username'].lower().strip()
        chat_id = message['chat']['id']
    except Exception as e:
        logging.error(f'Ошибка в строке 24 echobot.py: {e}.')
        return

    chat = Chat()
    chat.set_uc(username, chat_id)

    firms = []
    manager = []
    output = get_data()
    try:
        manager = output[0].get('manager', [])
    except Exception:
        logging.error(f'Ошибка получения данных по индексу 0 output={output}.')
        manager = []

    if username in manager:
        # Если пользователь менеджер, то показваем всех юридических лиц.
        for item in output:

            tmp_obj = dict()
            tmp_obj['id'] = item['id']
            tmp_obj['column'] = item['column']
            tmp_obj['name'] = item['name']

            firms.append(tmp_obj)
    else:
        for item in output:
            for ac in item['im']:
                if ac == username:

                    tmp_obj = dict()
                    tmp_obj['id'] = item['id']
                    tmp_obj['name'] = item['name']
                    tmp_obj['column'] = item['column']

                    firms.append(tmp_obj)
            # end for
        # end for
    if len(firms) == 0:
        r = ''
        for s in manager:
            r += '@' + str(s) + ' '
        r = r.strip()
        text = f'К вашему телеграмм аккаунту @{username} нет прикрепленных аккаунтов на фулфилменте. Обратитесь к менеджеру {r} для того, чтобы он добавил вас.'
        keyboard = [
        [
            InlineKeyboardButton('Меня добавили', callback_data='333'),
        ],]
    
        reply_markup = InlineKeyboardMarkup(keyboard)
        message.reply_text(text, reply_markup=reply_markup)

    if len(firms) > 0:
        message.reply_text(prompt, reply_markup=firms_btns(firms), parse_mode=ParseMode.MARKDOWN)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    query.answer()
    btn_data = query.data

    if btn_data == '333':
        # Нажата кнопка 'Меня добавили'
        get_info(update, context)
        return
        
    if btn_data.startswith('f'):
        # Нажата кнопка 'ИП Иванов И. И.'
        f_letter, column = btn_data.split('_')
        column = int(column)
        firm = get_firm(column)
        uid = firm['id']
        bt = get_text_balance(firm)
        text = f'✅ Вы выбрали *{firm["name"]}*.\n{bt}'
        update.callback_query.message.reply_text(text, reply_markup=actions_btns(firm), parse_mode=ParseMode.MARKDOWN)
        return

    if btn_data.startswith('t'):
        # Нажата кнопка установки времени рассылки.
        t_letter, column, hour = btn_data.split('_')
        column = int(column)
        hour = int(hour)
        firm = get_firm(column)
        uid = firm['id']
        
        c_obj = Conf()
        c_obj.set_hour(uid, hour)
        
        reply_markup = actions_btns(firm)
        hour_str = str(hour).zfill(2)
        hour_str = f'{hour_str}:00'

        text = f'⏰ Вы выбрали время уведомлений *{hour_str}* для {firm["name"]}.'
        update.callback_query.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    column, action = btn_data.split('_')
    column = int(column)
    
    firm = get_firm(column)
    name = firm['name']
    uid = firm['id']

    if action == '1':
        text = get_text_balance(firm)

    if action == '2':
        mid = firm['id']
        name = firm['name']
        column = firm['column']
        uid = firm['id']

        c_obj = Conf()
        config = c_obj.get_conf(uid)

        if config.get('is_send'):
            c_obj.set_send(uid, False)
            text = f'🔕 Вы отключили уведомления о блокировках и напоминания об оплате услуг для {name}.'
        else:
            c_obj.set_send(uid, True)
            text = f'✅ Вы включили уведомления о блокировках и напоминания об оплате услуг для {name}.'

        text = f"""\n
{text}
"""
    if action == '3':
        # Нажата кнопка 'Установить время рассылки'        
        uid = firm['id']

        c_obj = Conf()
        config = c_obj.get_conf(uid)
        hour = config.get('hour')
        text = f'Сейчас вы получаете уведомления в *{hour}:00*.\n\n⏰ Выберите время рассылки для {name}.'
        update.callback_query.message.reply_text(text, reply_markup=timer_btns(firm), parse_mode=ParseMode.MARKDOWN)
        return

    if action == '4':
        # Нажата кнопка 'Сменить аккаунт'
        text = f'Вам доступна информация об этих аккаунтах:'
        get_info(update, context, prompt=text)
        return

    if action == '5':
        # Нажата кнопка «Отгрузки» и «Полки» за последний месяц
        uid = firm['id']
        date_shipments_shelves = firm['date_shipments_shelves']
        text = filter_current_month(date_shipments_shelves)

    update.callback_query.message.reply_text(
        text,
        reply_markup=actions_btns(firm),
        parse_mode=ParseMode.MARKDOWN
    )


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, workers=4)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", get_info))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
