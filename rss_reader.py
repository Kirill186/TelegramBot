import feedparser
import requests


def get_rss_feed(channel):
    try:
        response = requests.get(channel)
        response.raise_for_status()  # Проверяем, что запрос успешен
        feed = feedparser.parse(response.content)

        articles = []
        for entry in reversed(feed.entries):
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'id': entry.link  # Используем ссылку как уникальный ID
            })
        return articles

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе RSS-ленты: {e}")
        return []
