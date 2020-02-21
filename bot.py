import os
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta
import sched
import threading
import json

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

permissionsID = 393253446, 531381261
homework_from_file = {}
buffer = {}

time_of_lessons = [(830, 1005),
                   (1025, 1200),
                   (1220, 1355),
                   (1415, 1550)]

tz = timezone(timedelta(hours=2))
first_week = datetime(2020, 2, 1, tzinfo=tz)


def get_date():
    date = datetime.now(tz=tz)
    # date = datetime(2020, 2, 12, tzinfo=tz)
    today, time_now = date.strftime('%d.%m %H%M').split(' ')
    time_now = int(time_now)
    day_of_week = date.weekday()
    weeks_past = (date - first_week).days // 7
    even_week = weeks_past % 2
    return time_now, day_of_week, even_week


def get_num_of_lesson():
    num_of_lesson = -1
    time_now = int(datetime.now(tz=tz).strftime('%H%M'))

    for start, end in time_of_lessons:
        num_of_lesson += 1
        if time_now < end:
            break
    else:
        return
    return num_of_lesson


@bot.message_handler(commands=['now'])
def send_now(message: Message):
    # Get the number of current or upcoming lesson
    num_of_lesson = get_num_of_lesson()

    # If NoneType is returned
    if not num_of_lesson:
        bot.send_message(message.chat.id, '*Пари закінчились*', parse_mode='Markdown')
        return

    # Get all necessary information about today
    time_now, day_of_week, even_week = get_date()
    try:
        lessons_today = sched.DICT[str(even_week + 1)][day_of_week]
    # Day of week Sat or Sun
    except KeyError:
        bot.send_message(message.chat.id, '*Сьогодні вихідний*', parse_mode='Markdown')
        return

    # Information about current lesson and time of begin and end of it
    lesson_now = lessons_today[num_of_lesson]
    start, end = time_of_lessons[num_of_lesson]

    # Mean 60 minutes format
    hours_difference = abs((time_now // 100 - start // 100) * 40)

    if time_now > start:
        time_left = time_now - start - hours_difference
        time_string = f'Минуло {time_left} хв. пари.'
    else:
        time_left = start - time_now - hours_difference
        time_string = f'Пара розпочнеться за {time_left} хв.'

    ans = '_' + time_string + '_\n'
    ans += '*Дисципліна*: \n  \u27A5 ' + lesson_now[0] + '\n'
    ans += '*Вид заняття*: \n  \u27A5 ' + lesson_now[-1] + '\n'
    ans += '*Викладач*: \n  \u27A5 ' + '\n'.join(lesson_now[1]) + '\n'
    ans += '*Локація*: \n  \u27A5 ' + lesson_now[2] + '\n'

    bot.send_message(message.chat.id, ans, parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def welcome(message):
    reply = "👋🏻 Привіт. Радий вітати тебе!\n" \
            "🤖 Це наш бот.\n\n📝 А наш староста завжди оновлює список дз.\n\n" \
            "⌨️ Використовуй команду /homework аби дізнатись актуальний список дз.\n" \
            "\n📕 Зі скаргами та пропозиціями писати @hladkky"
    with open('sticker.webp', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['homework'])
def send_homework(message):
    answer = ''
    with open('data.json', encoding='utf-8') as f:
        homework = json.load(f)
        for d, hw in homework.items():
            task_list = ''
            if not hw:
                task_list += '       -\n'
            else:
                for task, dates in hw.items():
                    task_list += f'   \u2756 *{task}*:\n    ' \
                                 f'    \u27A5   {dates}\n'
            answer += f'*{d}*:\n{task_list}\n'
    bot.send_message(message.chat.id, answer, parse_mode='Markdown')


def cancel_message(message):
    bot.reply_to(message, 'Відмінено', reply_markup=telebot.types.ReplyKeyboardRemove())
    return


# ===============================================================
# ---------------------- SETHOMEWORK STEPS ----------------------
@bot.message_handler(commands=['sethomework'])
def set_homework(message: Message):
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, 'Команда призначена для приватних повідомлень.')
    elif message.from_user.id not in permissionsID:
        bot.send_message(message.chat.id, 'Відсутні права доступу.')
    else:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
        markup.add(*(telebot.types.KeyboardButton(less) for less in sched.lessons))
        markup.add("Відмінити↩")
        msg = bot.send_message(message.chat.id, 'Дисципліна:', reply_markup=markup)
        bot.register_next_step_handler(msg, name_step)


def name_step(message):
    name_of_lesson = message.text
    if name_of_lesson == 'Відмінити↩':
        return cancel_message(message)

    if name_of_lesson not in sched.lessons:
        bot.reply_to(message, 'Предмет відсутній', reply_markup=telebot.types.ReplyKeyboardRemove())
        return

    buffer['name'] = name_of_lesson
    reply = 'Яку дію виконати?'
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('✅Додати', '♻Перезаписати', '❎Видалити', 'Відмінити↩')
    msg = bot.reply_to(message, text=reply, reply_markup=markup)
    bot.register_next_step_handler(msg, option_step)


def option_step(message):
    if message.text not in ('✅Додати', '♻Перезаписати', '❎Видалити'):
        return cancel_message(message)

    with open('data.json', encoding='utf-8') as f:
        global homework_from_file
        homework_from_file = json.load(f)

    buffer['tasks'] = homework_from_file[buffer['name']].copy()

    if message.text == '❎Видалити':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add('Усі завдання')
        markup.add(*(task for task in buffer['tasks']))
        msg = bot.send_message(message.chat.id, 'Оберіть завдання:', reply_markup=markup)
        return bot.register_next_step_handler(msg, choose_delete_task)
    elif message.text == '♻Перезаписати':
        buffer['tasks'] = {}
    msg = bot.send_message(message.chat.id,
                           text='Нове завдання:',
                           reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, new_task_step)


def choose_delete_task(message):
    if message.text == 'Усі завдання':
        buffer['tasks'] = {}
    else:
        try:
            del buffer['tasks'][message.text]
        except KeyError:
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add('Усі завдання')
            markup.add(*(task for task in buffer['tasks']))
            m = bot.send_message(message.chat.id, 'Оберіть завдання серед запропонованих:', reply_markup=markup)
            return bot.register_next_step_handler(m, choose_delete_task)

    homework_from_file[buffer['name']] = buffer['tasks']
    submit_changes()
    bot.send_message(message.chat.id,
                     text='Успішно видалено!',
                     reply_markup=telebot.types.ReplyKeyboardRemove())


def new_task_step(message):
    buffer['new_task'] = message.text
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    date = datetime.today()
    list_of_dates = []
    for i in range(14):
        date += timedelta(days=1)
        item_date, item_weekday = date.strftime('%d.%m %w').split()
        if int(item_weekday) <= 4:
            list_of_dates.append(f'{item_date} {sched.weekdays[int(item_weekday)]}')
    markup.add(*list_of_dates)
    bot.send_message(message.chat.id,
                     text="Укажіть дату заданого завдання:",
                     reply_markup=markup)
    bot.register_next_step_handler(message, set_date)


def set_date(message):
    homework_from_file[buffer['name']][buffer['new_task']] = message.text.split()[0]
    submit_changes()
    bot.send_message(message.chat.id, text='Успішно оновлено!',
                     reply_markup=telebot.types.ReplyKeyboardRemove)


def submit_changes():
    global buffer
    del buffer
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(homework_from_file, f, ensure_ascii=False, indent=4)
    buffer = {}
# ---------------------- SETHOMEWORK END ----------------------
# ===============================================================


@bot.message_handler(commands=['today', 'tomorrow'])
def send_today_schedule(message: Message):
    time_now, day_of_week, even_week = get_date()
    date = datetime.today()
    if '/tomorrow' in message.text:
        day_of_week = (day_of_week + 1) % 7
        date += timedelta(days=1)
    day, month = date.strftime('%d %m').split()
    ans = '🗓{0} {1}\n\n'.format(day, sched.months[int(month) - 1])
    if day_of_week == 5 or day_of_week == 6:
        bot.send_message(message.chat.id, text='*Вихідний*', parse_mode='Markdown')
    else:
        week = list(sched.DICT.keys())[even_week]
        ans += f'🔑 *{week} ТИЖДЕНЬ*\n\n'
        ans += '🔎 *' + sched.weekdays[day_of_week] + '*\n'
        i = 1
        for full_day in sched.DICT[str(even_week+1)][day_of_week]:
            ans += f'❇{i}. ' if get_num_of_lesson() == i-1 else f'      {i}. '
            ans += full_day[0]
            ans += '\n           🏢 ' if full_day[2] != '' else ''
            ans += '_' + full_day[2] + '_'
            ans += '\n           📨 ' if full_day[2] != '' else ''
            ans += '_' + full_day[3] + '_\n'
            i += 1
        bot.send_message(message.chat.id, text=ans, parse_mode='Markdown')


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    ans = ''
    for week, days in sched.DICT.items():
        ans += f'🔑 *{week} ТИЖДЕНЬ*\n\n'
        for weekday, full_list in days.items():
            ans += (f'🔸 *{sched.weekdays[weekday]}*' + '\n')
            for i in range(len(full_list)):
                ans += str(i+1)+'. '
                ans += full_list[i][0]
                ans += '\n          ' if full_list[i][-1] != '' else ''
                ans += f'_{full_list[i][-1]}_' + '\n'
            ans += '\n'
        ans += '\n'

    bot.send_message(message.chat.id,
                     text=ans,
                     parse_mode='Markdown')


@bot.message_handler(commands=['teachers'])
def send_teachers(message):
    ans = '*ВИКЛАДАЧІ* \n\n'
    for i in range(len(sched.lessons)):
        ans += '\u2771 _' + sched.lessons[i] + '_\n'
        for teacher in sched.teachers[i]:
            ans += '  \u274F '
            ans += teacher + '\n'
        ans += '\n'
    bot.send_message(message.chat.id,
                     text=ans,
                     parse_mode='Markdown')


bot.polling()
# ================================================

# def cycle():
#
#
#
# def run_bot():
#     with open('data.json', encoding='utf-8') as f:
#         d2 = json.load(f)
#         while 1:
#             print(2)


# ================================================
# t1 = threading.Thread(target=run_bot)
# t2 = threading.Thread(target=cycle)
#
# # starting thread 1
# t1.start()
# # starting thread 2
# t2.start()
