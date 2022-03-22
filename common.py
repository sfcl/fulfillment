import json
import logging
import os
import pathlib
import time

import gspread

from conf import URL


def str2money(val):
    val = val.replace('₽', '')
    val = ''.join(val.split())
    try:
        val = int(val)
    except:
        val = 0
    return val


def _get_worksheet():
    gc = gspread.service_account(filename='key.json')

    error_count = 0
    while True:
        try:
            sh = gc.open_by_url(URL)
        except Exception as error:
            error_count += 1
            error = str(error)
            logging.info(f'Ошибка открытия ГуглТаблицы: {error}. Счетчик ошибки {error_count}.')
            if error_count == 5:
                return None
            continue
        else:
            break
    
    worksheet = sh.worksheets()[0]
    return worksheet


def get_firm(column):
    """
    Получение данных об одном юр. лице из таблицы.
    """
    start_column = column
    firm = {
        'id': '3333abc',
        'name': '',
        'to_store': 0,
        'to_shipping': 0,
        'balance': 0,
        'treshold': 0,
        'day': '',
        'tels': '',
        'im': '',
        'manager': '',
        'column': start_column,
        'for_14_days': 0, # указано количество денег, потраченных за 14 дней
    }
    worksheet = _get_worksheet()

    if worksheet is None:
        return firm

    list_of_lists = worksheet.get_all_values()
    list_of_lists = list(zip(*list_of_lists))

    column = list_of_lists[column][0:14]

    manager = list_of_lists[0][12] # Ячейка A13
    manager = manager.split(',')
    manager = [i.lower().strip() for i in manager]

    mid = column[1]

    if mid == '':
        return firm

    name = column[2]
    to_store = str2money(column[4])
    to_shipping = str2money(column[6])
    balance = str2money(column[8])
    tr = str2money(column[9])
    day = column[10]
    tel = column[11]
    im = column[12].split(',')
    im = [i.lower().strip() for i in im]
    for_14_days = str2money(column[13])

    date_shipments_shelves  = list(zip(
        list_of_lists[0][15:],
        list_of_lists[start_column][15:],
        list_of_lists[start_column+1][15:]
    ))

    firm = {
        'id': mid,
        'name': name,
        'to_store': to_store,
        'to_shipping': to_shipping,
        'balance': balance,
        'treshold': tr,
        'day': day,
        'tels': tel,
        'im': im,
        'manager': manager,
        'column': start_column,
        'for_14_days': for_14_days,
        'date_shipments_shelves': date_shipments_shelves,
    }
    return firm


def get_data():
    """
    Получение всех данных юр. лиц из таблицы.
    """
    output = []
    worksheet = _get_worksheet()

    if worksheet is None:
        return output      

    start_cell = 5 # Начало с буквы F, нумерация с 0.
    
    # Больше к Гугл Таблицам не обращаемся.
    list_of_lists = worksheet.get_all_values()
    list_of_lists = list(zip(*list_of_lists))

    manager = list_of_lists[0][12] # Ячейка A13
    manager = manager.split(',')
    manager = [i.lower().strip() for i in manager]

    while True:
        column = list_of_lists[start_cell][0:14]
        mid = column[1]

        if mid == '':
            break

        name = column[2]
        to_store = str2money(column[4])
        to_shipping = str2money(column[6])
        balance = str2money(column[8])
        tr = str2money(column[9])
        day = column[10]
        tel = column[11]
        im = column[12].split(',')
        im = [i.lower().strip() for i in im]
        for_14_days = column[13]

        if mid == '12FFВк':
            im.append('mypy2000')

        output.append({
            'id': mid,
            'name': name,
            'to_store': to_store,
            'to_shipping': to_shipping,
            'balance': balance,
            'treshold': tr,
            'day': day,
            'tels': tel,
            'im': im,
            'manager': manager,
            'column': start_cell,
            'for_14_days': for_14_days,
        })
        start_cell += 2

    return output


def pretty_day(day):
    day = str(day)
    if day == '':
        return '0 дней'
    if day == '0':
        return '0 дней'
    if day == '1':
        return '1 день'
    if day == '2':
        return '2 дня'
    if day == '3':
        return '3 дня'
    if day == '4':
        return '4 дня'
    return f'{day} дней'


class Conf:
    def __init__(self):
        base_path = pathlib.Path().resolve()
        self.db_dir = os.path.join(base_path, 'db')
        if not os.path.isdir(self.db_dir):
            os.makedirs(self.db_dir)

    def get_conf(self, uid):
        file_name = os.path.join(self.db_dir, f'{uid}.json')
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                config = json.load(f)
            hour = config.get('hour', 11)
            is_send = config.get('is_send', True)
            return {'hour': hour, 'is_send': is_send}
        else:
            return {'hour': 11, 'is_send': True}
    
    def set_hour(self, uid, hour):
        file_name = os.path.join(self.db_dir, f'{uid}.json')

        if os.path.isfile(file_name):
             with open(file_name, 'r') as f:
                config = json.load(f)
             config['hour'] = hour
             
             with open(file_name, 'w') as f:
                json.dump(config, f)
        else:
            config = {'hour': hour, 'is_send': True}

            with open(file_name, 'w') as f:
                json.dump(config, f)
                
    def set_send(self, uid, is_send):
        file_name = os.path.join(self.db_dir, f'{uid}.json')

        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                config = json.load(f)
            config['is_send'] = is_send
 
            with open(file_name, 'w') as f:
                json.dump(config, f)
        else:
            config = {'hour': 11, 'is_send': is_send}

            with open(file_name, 'w') as f:
                json.dump(config, f)

class Chat:
    def __init__(self):
        base_path = pathlib.Path().resolve()
        self.db_dir = os.path.join(base_path, 'db')
        if not os.path.isdir(self.db_dir):
            os.makedirs(self.db_dir)

    def set_uc(self, username, chat_id):
        file_name = os.path.join(self.db_dir, 'chat.json')
        change_flag = False
        if os.path.isfile(file_name):    
            config = dict()
            with open(file_name, 'r') as f:
                config = json.load(f)

            if config.get(username):
                chats_ids = config.get(username, [])
                if chat_id in chats_ids:
                    change_flag = False
                else:
                    chats_ids.append(chat_id)
                    change_flag = True
                config[username] = chats_ids
            else:
                change_flag = True
                config[username] = [chat_id,]
        else:
            change_flag = True
            config = dict()
            config[username] = [chat_id,]

        if change_flag:
            with open(file_name, 'w') as f:
                json.dump(config, f)

    def get_all(self):
        file_name = os.path.join(self.db_dir, 'chat.json')
        config = dict()
        if os.path.isfile(file_name):
            config = dict()
            with open(file_name, 'r') as f:
                config = json.load(f)
        return config

