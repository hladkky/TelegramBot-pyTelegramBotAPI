import telebot
from telebot.types import Message
from datetime import datetime


TOKEN = '731991040:AAHKCcrcVRKDYvrPyupl8COe0JLLYtaKHk8'
bot = telebot.TeleBot(TOKEN)

permissionsID = 393253446, 531381261
bmd = 'Обробка та аналіз БМД'
web = 'Веб-технології та веб-дизайн'
cm = 'Чисельні методи'
oop = 'ООП'
bi = 'Біоінформатика-1. Основи МББ'
en = 'Іноземна мова'
homework = {bmd: None,
            web: None,
            cm: None,
            oop: None,
            bi: None,
            en: None}
buffer = {}

first_saturday = datetime(2020, 1, 18)


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
        if not hw:
            hw = '-'
        answer += f'*{d}*:\n   {hw}\n'
    bot.send_message(message.chat.id, answer, parse_mode='Markdown')


@bot.message_handler(commands=['sethomework'])
def set_homework(message: Message):
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, 'Команда доступна в приватних повідомленнях.')
    elif message.from_user.id not in permissionsID:
        bot.send_message(message.chat.id, 'Відсутні права доступу.')
    else:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(bmd, web, cm, oop, bi, en)
        msg = bot.send_message(message.chat.id, 'Дисципліна:', reply_markup=markup)
        bot.register_next_step_handler(msg, name_step)


def name_step(message):
    name = message.text
    if name not in homework.keys():
        bot.reply_to(message, 'Предмет відсутній', reply_markup=telebot.types.ReplyKeyboardRemove())
        return
    buffer['name'] = name
    print(buffer)
    reply = 'Додати, перезаписати, видалити?'
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Додати', 'Перезаписати', 'Видалити')
    msg = bot.reply_to(message, text=reply, reply_markup=markup)
    bot.register_next_step_handler(msg, set_step)


def set_step(message):
    if message.text == 'Видалити':
        homework[buffer['name']] = None
        bot.send_message(message.chat.id,
                         text='Успішно видалено!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    else:
        buffer['mode'] = message.text
        msg = bot.send_message(message.chat.id,
                               text='Нове завдання:',
                               reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, new_task_step)


def new_task_step(message):
    discipline = buffer['name']
    if not homework[discipline]:
        homework[discipline] = message.text
    else:
        rewrite = 1 if buffer['mode'] == 'Перезаписати' else 0
        if rewrite:
            homework[discipline] = message.text
        else:
            homework[discipline] += f'\n   {message.text}'
    bot.send_message(message.chat.id,
                     text='Успішно оновлено!',
                     reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['today', 'tomorrow'])
def send_today_schedule(message: Message):
    day_of_week = datetime.today().weekday()
    current_week = ((datetime.today() - first_saturday).days // 7) % 2
    if '/tomorrow' in message.text:
        day_of_week += 1
    if day_of_week == 5 or day_of_week == 6:
        bot.send_message(message.chat.id, text='*Вихідний*', parse_mode='Markdown')
    else:
        # numOfDay
        with open('schedule.txt', encoding='utf-8') as f:
            received_schedule = f.readlines()
            answer = received_schedule[28 * current_week] + '\n'

            for numOfLine in range(5):
                answer += received_schedule[2 + 5 * day_of_week + 28 * current_week + numOfLine]

            bot.send_message(message.chat.id, text=answer, parse_mode='Markdown')


@bot.message_handler(commands=['time'])
def send_schedule(message):

    print(message.from_user)

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