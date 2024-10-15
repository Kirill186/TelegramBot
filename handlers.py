import telebot
from config import BOT_TOKEN
from database import Database

bot = telebot.TeleBot(BOT_TOKEN)
db = Database('rss_channels.json')

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
    db.add_channel(user_id, channel_url)
    bot.reply_to(message, f"Канал {channel_url} был добавлен.")

@bot.message_handler(commands=['list'])
def list_channels(message):
    user_id = message.from_user.id
    channels = db.get_channels(user_id)
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
    db.remove_channel(user_id, channel_url)
    bot.reply_to(message, f"Канал {channel_url} был удален.")
