import time
from rss_reader import get_rss_feed
from handlers import bot
from database import Database


db = Database('rss_channels.json')


def check_rss_feeds():
    while True:
        for user_id in db.data.keys():
            channels = db.get_channels(user_id)
            for channel in channels:
                articles = get_rss_feed(channel)
                for article in articles:
                    # Отправляем сообщения, если они новые
                    bot.send_message(user_id, f"{article['title']}\n{article['link']}")
        time.sleep(300)  # Проверять каждые 5 минут


if __name__ == '__main__':
    from threading import Thread
    Thread(target=check_rss_feeds).start()  # Запускаем проверку в отдельном потоке
    bot.polling(none_stop=True, interval=0)
