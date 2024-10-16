import time
from datetime import datetime
from rss_reader import get_rss_feed, load_last_check_time, save_last_check_time
from handlers import bot, db


def check_rss_feeds():
    last_check_time = load_last_check_time()
    while True:
        # Получаем всех пользователей и их каналы из базы данных
        users = db.get_all_users_and_channels()

        for user_id, channels in users:
            for channel in channels:
                articles = get_rss_feed(channel)  # Получаем RSS-ленту для канала
                for article in articles:

                    # Отправляем новые статьи
                    published_time = datetime.strptime(article['published'], '%Y-%m-%dT%H:%M:%SZ')

                    if last_check_time is None or published_time > last_check_time:
                        bot.send_message(user_id, f"{article['title']}\n{article['link']}")

        save_last_check_time(datetime.utcnow())
        time.sleep(300)  # Проверяем каждые 5 минут


if __name__ == '__main__':
    from threading import Thread
    Thread(target=check_rss_feeds).start()  # Запускаем проверку в отдельном потоке
    try:
        bot.polling(none_stop=True)
    finally:
        db.close()  # Закрываем соединение с базой данных
