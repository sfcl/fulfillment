import datetime
import json
import logging
import os

import telegram

from buttons import actions_btns, firms_btns, timer_btns
from common import get_data, get_firm, Conf, Chat, pretty_day
from text_proc import money
from conf import TOKEN


def send(bot, message, firm):
    im = firm['im']
    for username in im:
        logging.error(f'Send message: {username} {message}.')
        chat_obj = Chat()
        chats_dict = chat_obj.get_all()
        if chats_dict.get(username):
            for cid in chats_dict.get(username):
                bot.send_message(
                    chat_id=cid,
                    text=message,
                    reply_markup=actions_btns(firm),
                    parse_mode=telegram.ParseMode.MARKDOWN
                )
    return None


def main() -> None:
    """
    Функция для вызова каждый час.
    """
    bot = telegram.Bot(token=TOKEN)
    now = datetime.datetime.now().time()
    output = get_data()
    #logging.error(f'now= {now}. output= {output}.')
    # При наступлении нового часа ищем пользователей, кому нужно отправлять сообщения.
    output = get_data()
    for item in output:
        uid = item['id']
        c_obj = Conf()
        config = c_obj.get_conf(uid)

        if not config['is_send']:
            continue
            
        if config['hour'] != now.hour:
            continue

        if item['balance'] == 'Ошибка':
            continue

        if item['treshold'] == 'Ошибка':
            continue

        name = item['name']
        balance = item['balance']
        day = item['day']
        im = item['im']

        common_txt = '_Вы можете отключить уведомления или назначить их на другое время._'
        if balance < 0:
            balance = money(balance)
            message = f'❌ {name}, на вашем счёте образовалась задолженность *{balance} ₽, отгрузки остановлены*, просьба срочно пополнить счёт.\n\n{common_txt}'
            send(bot, message, item)

        elif balance == 0:
            balance = money(balance)
            message = f'❌ {name} на вашем счёте *0 ₽*. Для *начала отгрузок*, пожалуйста, пополните счёт.\n\n{common_txt}'
            send(bot, message, item)

        else:
            if balance < item['treshold']:
                day = pretty_day(day)
                balance = money(balance)
                message = f'❌ {name}, на вашем счете осталось меньше *{balance} ₽*. Этого хватит примерно на *{day} до блокировки*.\n\n{common_txt}'
                send(bot, message, item)

    # end def


if __name__ == '__main__':
    main()
