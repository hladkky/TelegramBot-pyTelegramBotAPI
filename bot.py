import telebot
from telebot.types import Message
from datetime import datetime

TOKEN = '731991040:AAHKCcrcVRKDYvrPyupl8COe0JLLYtaKHk8'
bot = telebot.TeleBot(TOKEN)

idChat = '531381261'


first_saturday = datetime(2020, 1, 18)


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