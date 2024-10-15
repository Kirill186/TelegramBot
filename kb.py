from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_news_categories_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Технологии", callback_data="news_tech"))
    markup.add(InlineKeyboardButton("Политика", callback_data="news_politics"))
    markup.add(InlineKeyboardButton("Спорт", callback_data="news_sports"))
    return markup
