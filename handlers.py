import telebot
from telebot import types
from rss_reader import get_rss_feed
from dotenv import load_dotenv
import os
from database import Database


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

bot = telebot.TeleBot(BOT_TOKEN)
db = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_channel_button = types.KeyboardButton("➕ Добавить канал")
    remove_channel_button = types.KeyboardButton("➖ Удалить канал")
    list_channel_button = types.KeyboardButton("Мои каналы")
    markup.add(add_channel_button, remove_channel_button, list_channel_button)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message,
        "Привет! Я бот для получения новостей из RSS-каналов. Выберите действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "➕ Добавить канал")
def add_channel_prompt(message):
    bot.reply_to(message, "Введите Канал, который вы хотите добавить:")
    bot.register_next_step_handler(message, process_add_channel)

def process_add_channel(message):
    user_id = message.from_user.id
    channel_url = message.text
    try:
        db.add_channel(user_id, channel_url)
        bot.reply_to(message, f"Канал {channel_url} был добавлен.", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f"Возникла ошибка при добавлении канала: {e}", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "➖ Удалить канал")
def remove_channel_prompt(message):
    bot.reply_to(message, "Введите URL RSS-канала, который вы хотите удалить:")
    bot.register_next_step_handler(message, process_remove_channel)

def process_remove_channel(message):
    user_id = message.from_user.id
    channel_url = message.text
    try:
        db.remove_channel(user_id, channel_url)
        bot.reply_to(message, f"Канал {channel_url} был удален.", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f"Возникла ошибка при удалении канала: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "Мои каналы")
def list(message):
    user_id = message.from_user.id
    channels = db.get_channels(user_id)

    if not channels:
        bot.reply_to(message, "У вас нет добавленных RSS-каналов.")
        return

    keyboard = types.InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(types.InlineKeyboardButton(text=channel, callback_data=f"get_rss_{channel}"))

    bot.reply_to(message, "Выберите канал для получения RSS:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('get_rss_'))
def send_rss(call):
    channel_url = call.data.split('_', 2)[2]  # Извлекаем URL канала
    articles = get_rss_feed(channel_url)  # Получаем статьи из RSS

    if articles:
        for article in articles:
            bot.send_message(call.message.chat.id, f"{article['title']}\n{article['link']}")

    else:
        bot.send_message(call.message.chat.id, "Нет доступных статей в этом RSS-канале.")