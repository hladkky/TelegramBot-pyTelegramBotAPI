import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta
import sched
from sched import bmd, web, cm, oop, bi, en

TOKEN = '731991040:AAHKCcrcVRKDYvrPyupl8COe0JLLYtaKHk8'
bot = telebot.TeleBot(TOKEN)

permissionsID = 393253446, 531381261

homework = {bmd: {},
            web: {},
            cm: {},
            oop: {},
            bi: {},
            en: {}}
buffer = {}

time_of_lessons = [(830, 1005),
                   (1025, 1200),
                   (1220, 1355),
                   (1415, 1550)]

tz = timezone(timedelta(hours=2))
first_week = datetime(2020, 2, 1, tzinfo=tz)


def get_date():
    date = datetime.now(tz=tz)
    today, time_now = date.strftime('%d.%m %H%M').split(' ')
    time_now = int(time_now)
    day_of_week = date.weekday()
    weeks_past = (date - first_week).days // 7
    even_week = weeks_past % 2
    return time_now, day_of_week, even_week


@bot.message_handler(commands=['now'])
def send_now(message: Message):
    time_now, day_of_week, even_week = get_date()
    num_of_lesson = -1
    try:
        lessons_today = sched.DICT[str(even_week+1)][day_of_week]
    except KeyError:
        bot.send_message(message.chat.id, '*Сьогодні вихідний*', parse_mode='Markdown')
        return

    for start, end in time_of_lessons:
        num_of_lesson += 1
        if time_now < end:
            break
    else:
        bot.send_message(message.chat.id, '*Пари закінчились*', parse_mode='Markdown')
        return

    try:
        lesson_now = lessons_today[num_of_lesson]
    except IndexError:
        bot.send_message(message.chat.id, '*Пари закінчились*', parse_mode='Markdown')
        return

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
    reply = "Привіт. Радий вітати тебе!\n" \
            "Це наш бот.\n\nА наш староста завжди оновлює список дз.\n\n" \
            "Використовуй команду /homework аби дізнатись актуальний список дз.\n" \
            "\nЗі скаргами та пропозиціями писати @hladkky"
    with open('sticker.webp', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['homework'])
def send_homework(message):
    answer = ''
    for d, hw in homework.items():
        task_list = ''
        if not hw:
            task_list += '    -\n'
        else:
            for task, dates in hw.items():
                task_list += f'   \u2756 *{task}*:\n    ' \
                             f'    \u27A5   {dates}\n'
        answer += f'*{d}*:\n{task_list}\n'
    bot.send_message(message.chat.id, answer, parse_mode='Markdown')


# ---------------------- SETHOMEWORK STEPS ----------------------
@bot.message_handler(commands=['sethomework'])
def set_homework(message: Message):
    if message.from_user.id not in permissionsID:
        bot.send_message(message.chat.id, 'Відсутні права доступу.')
    else:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(bmd, web, cm, oop, bi, en)
        msg = bot.send_message(message.chat.id, 'Дисципліна:', reply_markup=markup)
        bot.register_next_step_handler(msg, name_step)


def name_step(message):
    name = message.text
    if name not in homework.keys():
        bot.reply_to(message, 'Предмет відсутній', reply_markup=telebot.types.ReplyKeyboardRemove())
        return
    buffer['name'] = name
    reply = 'Додати, перезаписати, видалити?'
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Додати', 'Перезаписати', 'Видалити')
    msg = bot.reply_to(message, text=reply, reply_markup=markup)
    bot.register_next_step_handler(msg, set_step)


def set_step(message):
    if message.text == 'Видалити':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add('Усі завдання')
        for task in homework[buffer['name']]:
            markup.add(task)
        msg = bot.send_message(message.chat.id, 'Оберіть завдання:', reply_markup=markup)
        bot.register_next_step_handler(msg, choose_delete_task)
        return
    elif message.text == 'Перезаписати':
        homework[buffer['name']] = {}
    msg = bot.send_message(message.chat.id,
                           text='Нове завдання:',
                           reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, new_task_step)


def choose_delete_task(message):
    discipline = buffer['name']
    if message.text == 'Усі завдання':
        homework[discipline] = []
    else:
        del homework[discipline][message.text]
    bot.send_message(message.chat.id,
                     text='Успішно видалено!',
                     reply_markup=telebot.types.ReplyKeyboardRemove())


def new_task_step(message):
    discipline = buffer['name']
    buffer['task'] = message.text

    markup = InlineKeyboardMarkup()

    item1 = InlineKeyboardButton('1')
    item2 = InlineKeyboardButton('2')

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     text="Укажіть одну або декілька дат для заданого завдання:",
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, set_date)


def set_date(message):
    discipline = buffer['name']
    task = buffer['task']
    homework[discipline][task] = message.text
    bot.send_message(message.chat.id, 'Успішно оновлено!')
# ---------------------- SETHOMEWORK END ----------------------


@bot.message_handler(commands=['today', 'tomorrow'])
def send_today_schedule(message: Message):
    time_now, day_of_week, even_week = get_date()
    if '/tomorrow' in message.text:
        day_of_week = (day_of_week + 1) % 7
    if day_of_week == 5 or day_of_week == 6:
        bot.send_message(message.chat.id, text='*Вихідний*', parse_mode='Markdown')
    else:
        week = list(sched.DICT.keys())[even_week]
        ans = f'\u275A *{week} ТИЖДЕНЬ*\n\n'
        ans += '*' + sched.weekdays[day_of_week] + '*\n'
        i = 1
        for full_day in sched.DICT[str(even_week+1)][day_of_week]:
            ans += '       ' + str(i) + '. ' + full_day[0]
            ans += ' \u21D2 ' if full_day[2] != '' else ''
            ans += '_' + full_day[2] + '_'
            ans += ' \u21D2 ' if full_day[2] != '' else ''
            ans += '_' + full_day[3] + '_\n'
            i += 1
        bot.send_message(message.chat.id, text=ans, parse_mode='Markdown')


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    ans = ''
    for week, days in sched.DICT.items():
        ans += f'\u275A *{week} ТИЖДЕНЬ*\n\n'
        for weekday, full_list in days.items():
            ans += (f'\u25FD *{sched.weekdays[weekday]}*' + '\n')
            for i in range (len(full_list)):
                ans += '  \u25B8  ' + str(i+1) + '. ' + full_list[i][0]
                ans += ' \u21D2 ' if full_list[i][-1] != '' else ''
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