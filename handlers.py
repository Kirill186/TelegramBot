from telebot import types
from rss_reader import get_rss_feed
import telebot
from dotenv import load_dotenv
import os
from database import Database


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
# DB_HOST = os.getenv('DB_HOST')
# DB_USER = os.getenv('DB_USER')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_NAME = os.getenv('DB_NAME')

bot = telebot.TeleBot(BOT_TOKEN)
db = Database()


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_channel_button = types.KeyboardButton("➕ Добавить канал")
    remove_channel_button = types.KeyboardButton("➖ Удалить канал")
    list_channel_button = types.KeyboardButton("Мои каналы")
    markup.add(add_channel_button, remove_channel_button, list_channel_button)
    return markup


def cancel_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Отменить"))
    return markup


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message,
        "Привет! Я бот для получения новостей из телеграмм-каналов. Выберите действие:",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "➕ Добавить канал")
def add_channel(message):
    bot.reply_to(message, "Введите название канала, который хотите добавить:", reply_markup=cancel_menu())
    bot.register_next_step_handler(message, process_add_channel)


def process_add_channel(message):
    if message.text == "Отменить":
        bot.reply_to(message, "Операция отменена.", reply_markup=main_menu())
        return

    user_id = message.from_user.id
    channel = message.text
    try:
        db.add_channel(user_id, channel)
        bot.reply_to(message, f"Канал {channel} был добавлен.", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f"Возникла ошибка при добавлении канала: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "➖ Удалить канал")
def remove_channel(message):
    user_id = message.from_user.id
    channels = db.get_channels(user_id)

    if not channels:
        bot.reply_to(message, "У вас нет добавленных каналов.", reply_markup=main_menu())
        return

    keyboard = types.InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(types.InlineKeyboardButton(text=channel, callback_data=f"remove_channel_{channel}"))

    bot.reply_to(message, "Выберите канал, который хотите удалить:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_channel_'))
def process_remove_channel_callback(call):
    user_id = call.message.chat.id
    channel_url = call.data.split('remove_channel_')[1]

    try:
        db.remove_channel(user_id, channel_url)

        bot.answer_callback_query(call.id, f"Канал {channel_url} удален.")

        bot.send_message(user_id, f"Канал {channel_url} был удален.", reply_markup=main_menu())
    except Exception as e:
        bot.send_message(user_id, f"Возникла ошибка при удалении канала: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "Мои каналы")
def channels_list(message):
    user_id = message.from_user.id
    channels = db.get_channels(user_id)

    if not channels:
        bot.reply_to(message, "У вас нет добавленных каналов.")
        return

    keyboard = types.InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(types.InlineKeyboardButton(text=channel, callback_data=f"get_rss_{channel}"))

    bot.reply_to(message, "Выберите канал для получения RSS:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get_rss_'))
def send_rss(call):
    channel_url = call.data.split('_', 2)[2]
    articles = get_rss_feed(channel_url)

    if articles:
        for article in articles:
            bot.send_message(call.message.chat.id, f"{article['link']}")

    else:
        bot.send_message(call.message.chat.id, "Нет доступных статей в этом канале.")