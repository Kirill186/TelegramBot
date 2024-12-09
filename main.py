from handlers import db, bot
import time
from datetime import datetime
from rss_reader import get_rss_feed


def check_rss_feeds():
    while True:
        try:
            users = db.get_all_users_and_channels()

            for user_id, channels in users:

                filters = db.get_filters(user_id)

                for channel in channels:
                    last_sent_time = db.get_last_sent_time(user_id, channel)
                    articles = get_rss_feed(channel)  # Получаем RSS-ленту для канала

                    new_articles = []

                    for article in articles:

                        # Проверяем, если статья новее последней рассылки
                        published_time = datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %Z')
                        if last_sent_time is None or published_time > datetime.fromisoformat(last_sent_time):

                            # Проверяем на наличие стоп-слов
                            if not any(word.lower() in article['title'].lower() for word in filters):
                                new_articles.append(article)

                    for article in new_articles:
                        bot.send_message(user_id, f"{article['link']}")

                    if new_articles:
                        db.update_last_sent_time(user_id, channel)
        except Exception as e:
            print(f"Ошибка при проверке RSS-ленты: {e}")

        time.sleep(300)  # Проверяем каждые 5 минут


if __name__ == '__main__':
    from threading import Thread
    Thread(target=check_rss_feeds).start()
    try:
        bot.polling(none_stop=True)
    finally:
        db.close()
