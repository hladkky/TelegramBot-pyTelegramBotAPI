import telebot
from telebot.types import Message
from datetime import datetime

TOKEN = '731991040:AAHKCcrcVRKDYvrPyupl8COe0JLLYtaKHk8'
bot = telebot.TeleBot(TOKEN)

permissionsID = 393253446, 531381261
bmd, web, cm, oop, bi, en = 'Обробка та аналіз БМД', 'Веб-технології та веб-дизайн',\
                            'Чисельні методи', 'ООП', 'Біоінформатика-1. Основи МББ', 'Іноземна мова'
homework = {bmd: {}, web: {}, cm: {}, oop: {}, bi: {}, en: {}}
buffer = {}

first_week = int(datetime(2020, 1, 18).strftime('%W'))


# Run while modification process
@bot.message_handler(func=lambda message: message.from_user.id != 531381261)
def work(message):
    if message.from_user.id != 531381261:
        bot.send_message(message.chat.id, text='Бот модифікується. Зачекайте ще трохи...')


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
            task_list += '\n   -'
        else:
            for task, date in hw.items():
                task_list += f'\n   *{task}*:\n   {date}'
        answer += f'*{d}*:   {task_list}\n'
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
    buffer['task']=message.text
    bot.send_message(message.chat.id,
                     text="Укажіть дедлайн вказаного завдання:",
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, set_date)


def set_date(message):
    discipline = buffer['name']
    task = buffer['task']
    homework[discipline][task] = f'    \u21b3 *{message.text}*'
    bot.send_message(message.chat.id, 'Успішно оновлено!')
# ---------------------- SETHOMEWORK END ----------------------


@bot.message_handler(commands=['today', 'tomorrow'])
def send_today_schedule(message: Message):
    current_week = int(datetime.today().strftime('%W'))
    day_of_week = datetime.today().weekday()
    if '/tomorrow' in message.text:
        day_of_week = (day_of_week + 1) // 8
    even_week = (current_week - first_week) % 2
    if day_of_week == 5 or day_of_week == 6:
        bot.send_message(message.chat.id, text='*Вихідний*', parse_mode='Markdown')
    else:
        # numOfDay
        with open('schedule.txt', encoding='utf-8') as f:
            received_schedule = f.readlines()
            answer = received_schedule[28 * even_week] + '\n'

            for numOfLine in range(5):
                answer += received_schedule[2 + 5 * day_of_week + 28 * even_week + numOfLine]

            bot.send_message(message.chat.id, text=answer, parse_mode='Markdown')


@bot.message_handler(commands=['time'])
def send_schedule(message):
    fmt = '%H:%M:%S'
    bot.reply_to(message, text=datetime.now().strftime(fmt))


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    with open('schedule.txt', encoding='utf-8') as f:
        textmessage = "*РОЗКЛАД* \n\n"
        received_schedule = f.readlines()
        for line in received_schedule:
            textmessage += line
        bot.send_message(message.chat.id,
                         text=textmessage,
                         parse_mode='Markdown')


@bot.message_handler(commands=['teachers'])
def send_teachers(message):
    with open('teachers.txt', encoding='utf-8') as f:
        answer = f.read()
        bot.send_message(message.chat.id,
                         text=answer,
                         parse_mode='Markdown')


bot.polling()