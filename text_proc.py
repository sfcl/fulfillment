from datetime import datetime


def filter_current_month(date_shipments_shelves):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentDay = datetime.now().day
    
    currentMonth = str(currentMonth)
    currentYear = str(currentYear)
    currentDay = str(currentDay)

    currentMonth = currentMonth.zfill(2)
    currentDay = currentDay.zfill(2)
    find_pattern = f'{currentDay}.{currentMonth}.{currentYear}'
    
    tmp_dates = []
    for line in date_shipments_shelves:
        tmp_dates.append(line)
        if line[0] == find_pattern:
            break

    tmp_dates = tmp_dates[-30:]

    output_text = '📄 Детализация событий на фулфилменте за последние 30 дней:\n\n'
    for line in tmp_dates:
        date = str(line[0])
        shipments = str(line[1])
        shelves = str(line[2])

        output_text += f'{date}. Отгрузок: {shipments}. Полок: {shelves}.\n'
    return output_text


def money(v):
    if not isinstance(v, int):
        return 0

    v = '{:,}'.format(v).replace(',', ' ')
    return v


def get_text_balance(firm):
    name = firm['name']
    balance = firm['balance']
    to_store = firm['to_store']
    to_shipping = firm['to_shipping']
    day = firm['day']
    for_14_days = firm['for_14_days']

    if balance <= 0:
        day_text = '❌ На вашем счету образовалась *задолженность*, отгрузки *остановлены*, пожалуйста, пополните счет.'
    else:
        day_text = f'Примерное количество дней до блокировки: {day}.'

    balance = money(balance)
    to_store = money(to_store)
    to_shipping = money(to_shipping)
    for_14_days = money(for_14_days)

    text=f"""
💳 На счету компании {name}:  *{balance} ₽*.
Из них {to_store} ₽ за хранение и {to_shipping} ₽ за отгрузку.\n
За последние 14 дней вы потратили {for_14_days} ₽.

{day_text}
"""
    return text

