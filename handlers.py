import telebot
from telebot import types
from rss_reader import get_rss_feed
from config import BOT_TOKEN, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from database import Database


bot = telebot.TeleBot(BOT_TOKEN)
db = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я бот для получения новостей из RSS-каналов. Используйте команду /add, чтобы добавить канал.")


@bot.message_handler(commands=['add'])
def add_channel(message):
    bot.reply_to(message, "Введите URL RSS-канала, который вы хотите добавить:")
    bot.register_next_step_handler(message, process_add_channel)


def process_add_channel(message):
    user_id = message.from_user.id
    channel_url = message.text
    try:
        db.add_channel(user_id, channel_url)
        bot.reply_to(message, f"Канал {channel_url} был добавлен.")

    except Exception as e:
        bot.reply_to(message, f"Возникла ошибка при добавлении канала")


@bot.message_handler(commands=['list'])
def list_channels(message):
    user_id = message.from_user.id
    channels = db.get_channels(str(user_id))
    if channels:
        response = "Ваши RSS-каналы:\n" + "\n".join(channels)
    else:
        response = "У вас нет добавленных RSS-каналов."
    bot.reply_to(message, response)


@bot.message_handler(commands=['remove'])
def remove_channel(message):
    bot.reply_to(message, "Введите URL RSS-канала, который вы хотите удалить:")
    bot.register_next_step_handler(message, process_remove_channel)


def process_remove_channel(message):
    user_id = message.from_user.id
    channel_url = message.text
    try:
        db.remove_channel(user_id, channel_url)
        bot.reply_to(message, f"Канал {channel_url} был удален.")

    except Exception as e:
        bot.reply_to(message, f"Возникла ошибка при удалении канала")


@bot.message_handler(commands=['getrss'])
def get_rss(message):
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
    print(f"Извлеченный URL канала: {channel_url}")
    articles = get_rss_feed(channel_url)  # Получаем статьи из RSS
    print(f"Полученные статьи: {articles}")

    if articles:
        for article in articles:
            bot.send_message(call.message.chat.id, f"{article['title']}\n{article['link']}")

    else:
        bot.send_message(call.message.chat.id, "Нет доступных статей в этом RSS-канале.")