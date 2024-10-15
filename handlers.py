from telebot import types
from kb import get_news_categories_keyboard
from news_aggregator import get_news_by_category


def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.send_message(message.chat.id, "Привет! Выбери категорию новостей:", reply_markup=get_news_categories_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('news_'))
    def handle_news_category(call):
        category = call.data.split('_')[1]
        news = get_news_by_category(category)
        for item in news:
            bot.send_message(call.message.chat.id, f"{item['title']}\n{item['url']}")
