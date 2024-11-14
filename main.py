import time
from datetime import datetime
from rss_reader import get_rss_feed
from handlers import bot, db


def check_rss_feeds():
    while True:
        # Получаем всех пользователей и их каналы из базы данных
        users = db.get_all_users_and_channels()

        for user_id, channels in users:
            for channel in channels:
                last_sent_time = db.get_last_sent_time(user_id, channel)
                articles = []
                # articles = get_rss_feed(channel)  # Получаем RSS-ленту для канала

                new_articles = []

                for article in articles:
                    # Проверяем, если статья новее последней рассылки

                    published_time = datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %Z')
                    if last_sent_time is None or published_time > datetime.fromisoformat(last_sent_time):
                        new_articles.append(article)

                for article in new_articles:
                    bot.send_message(user_id, f"{article['title']}\n{article['link']}")

                if new_articles:
                    db.update_last_sent_time(user_id, channel)

        time.sleep(300)  # Проверяем каждые 5 минут


if __name__ == '__main__':
    from threading import Thread
    Thread(target=check_rss_feeds).start()  # Запускаем проверку в отдельном потоке
    try:
        bot.polling(none_stop=True)
    finally:
        db.close()  # Закрываем соединение с базой данных
