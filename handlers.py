from telebot import types
from rss_reader import get_rss_feed
import telebot
from dotenv import load_dotenv
import os
from database import Database


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
db = Database()


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_channel_button = types.KeyboardButton("➕ Добавить канал")
    remove_channel_button = types.KeyboardButton("➖ Удалить канал")
    list_channel_button = types.KeyboardButton("Мои каналы")
    add_filter_button = types.KeyboardButton("➕ Добавить фильтр")
    remove_filter_button = types.KeyboardButton("➖ Удалить фильтр")
    list_filter_button = types.KeyboardButton("Мои фильтры")
    markup.add(add_channel_button, remove_channel_button, list_channel_button)
    markup.add(add_filter_button, remove_filter_button, list_filter_button)
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
    user_id = call.message.chat.id
    channel = call.data.split('_', 2)[2]

    articles = get_rss_feed(channel)
    filters = db.get_filters(user_id)
    if articles:
        for article in articles:
            if not any(word.lower() in article['title'].lower() for word in filters):
                bot.send_message(call.message.chat.id, f"{article['link']}")
                db.update_last_sent_time(user_id, channel)

    else:
        bot.send_message(call.message.chat.id, "Нет доступных статей в этом канале.")


@bot.message_handler(func=lambda message: message.text == "➕ Добавить фильтр")
def add_filter(message):
    bot.reply_to(message, "Введите слово или фразу для фильтрации новостей:", reply_markup=cancel_menu())
    bot.register_next_step_handler(message, process_add_filter)


def process_add_filter(message):
    if message.text == "Отменить":
        bot.reply_to(message, "Операция отменена.", reply_markup=main_menu())
        return

    user_id = message.from_user.id
    filter_word = message.text

    try:
        db.add_filter(user_id, filter_word)
        bot.reply_to(message, f"Фильтр \"{filter_word}\" добавлен.", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f"Ошибка при добавлении фильтра: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "➖ Удалить фильтр")
def remove_filter(message):
    user_id = message.from_user.id
    filters = db.get_filters(user_id)

    if not filters:
        bot.reply_to(message, "У вас нет добавленных фильтров.", reply_markup=main_menu())
        return

    keyboard = types.InlineKeyboardMarkup()
    for filter_word in filters:
        keyboard.add(types.InlineKeyboardButton(text=filter_word, callback_data=f"remove_filter_{filter_word}"))

    bot.reply_to(message, "Выберите фильтр для удаления:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_filter_'))
def process_remove_filter(call):
    filter_word = call.data.split('remove_filter_')[1]
    user_id = call.message.chat.id

    try:
        db.remove_filter(user_id, filter_word)
        bot.answer_callback_query(call.id, f"Фильтр \"{filter_word}\" удален.")
        bot.send_message(user_id, f"Фильтр \"{filter_word}\" успешно удален.", reply_markup=main_menu())
    except Exception as e:
        bot.send_message(user_id, f"Ошибка при удалении фильтра: {e}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "Мои фильтры")
def list_filters(message):
    user_id = message.from_user.id
    filters = db.get_filters(user_id)

    if not filters:
        bot.reply_to(message, "У вас нет добавленных фильтров.", reply_markup=main_menu())
        return

    filters_text = "\n".join(filters)
    bot.reply_to(message, f"Ваши фильтры:\n{filters_text}", reply_markup=main_menu())

