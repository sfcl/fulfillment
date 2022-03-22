import json
import logging
import os

from common import Conf

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


def actions_btns(firm):

    column = firm['column']
    uid = firm['id']

    c_obj = Conf()
    config = c_obj.get_conf(uid)

    if config.get('is_send'):
        btn_text = '🔕 Откл уведомления'
    else:
        btn_text = '✅ Вкл уведомления'

    keyboard = [
        [
            InlineKeyboardButton('💳 Узнать баланс', callback_data=f'{column}_1'),
            InlineKeyboardButton('📄 Детализация', callback_data=f'{column}_5'),
        ],[
            InlineKeyboardButton('⏳ Время уведомлений', callback_data=f'{column}_3'),
        ],[
            InlineKeyboardButton(btn_text, callback_data=f'{column}_2'),
        ],[
            InlineKeyboardButton('🔁 Сменить аккаунт', callback_data=f'{column}_4'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
    
    
def firms_btns(firms):
    
    keyboard = []
    for f in firms:
        column = f['column']
        name = f['name']
        
        keyboard.append([
            InlineKeyboardButton(f'☑️ {name}', callback_data=f'f_{column}'),
        ])
      
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def timer_btns(firm):
    
    keyboard = []
    row_buttons = []
    line_count = 1
    max_items_peer_line = 4
    for hour in range(24):
        column = firm['column']
        name = firm['name']
        hour_int = hour
        hour = str(hour).zfill(2)
        hour = f'{hour}:00'

        if line_count <= max_items_peer_line:
            row_buttons.append(InlineKeyboardButton(f'{hour}', callback_data=f't_{column}_{hour_int}'),)
            line_count += 1
        
        if line_count > max_items_peer_line:
            keyboard.append(row_buttons)
            row_buttons = []
            line_count = 1

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

