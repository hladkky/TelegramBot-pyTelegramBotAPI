import telebot
import schedule
import time
from telebot.types import Message
from datetime import datetime
from pytz import timezone

TOKEN = '731991040:AAHKCcrcVRKDYvrPyupl8COe0JLLYtaKHk8'
bot = telebot.TeleBot(TOKEN)

idChat = '531381261'

evenWeek = 1


def changeevenweek():
    global evenWeek
    evenWeek = 0 if evenWeek else 1


schedule.every().saturday.do(changeevenweek)


isEvenWeek = 5 * 6 * evenWeek - 2
dayOfWeek = datetime.today().weekday()


@bot.message_handler(commands=['today', 'tomorrow'])
def send_today_schedule(message: Message, day=dayOfWeek):
    with open('schedule.txt', encoding='utf-8') as f:
        if '/tomorrow' in message.text:
            day += 1

        if day == 5 or day == 6:
            bot.send_message(message.chat.id, text='*Вихідний*', parse_mode='Markdown')
        else:
            received_schedule = f.readlines()
            answer = received_schedule[isEvenWeek] + '\n'

            for numOfLine in range(5):
                answer += received_schedule[2 + 5 * day + isEvenWeek + numOfLine]

            bot.send_message(message.chat.id, text=answer, parse_mode='Markdown')


@bot.message_handler(commands=['time'])
def send_schedule(message):
    fmt = '%H:%M:%S'
    bot.reply_to(message, text=datetime.today(timezone('Europe/Kiev')).strftime(fmt))


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


while True:
    schedule.run_pending()
    time.sleep(1)