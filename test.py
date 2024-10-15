import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Токен от BotFather
TOKEN = '7891516257:AAGzFk6vCxAys5O4LsnjFNKBTw1M9DoZerQ'
bot = telebot.TeleBot(TOKEN)


# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем клавиатуру
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Кнопка 1")
    button2 = KeyboardButton("Кнопка 2")

    # Добавляем кнопки в клавиатуру
    markup.add(button1, button2)

    # Отправляем сообщение с reply-клавиатурой
    bot.send_message(message.chat.id, "Выбери кнопку:", reply_markup=markup)


# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    if message.text == "Кнопка 1":
        bot.send_message(message.chat.id, "Вы выбрали кнопку 1")
    elif message.text == "Кнопка 2":
        bot.send_message(message.chat.id, "Вы выбрали кнопку 2")


# Запуск бота
bot.polling()
