import feedparser
import requests


class RSSFetchError(Exception):
    """Ошибка получения RSS-канала"""
    pass

def get_rss_feed(channel):
    try:
        channel = "https://rsshub.app/telegram/channel/"+channel
        print(f"trying: {channel}")
        response = requests.get(channel, timeout=3)
        response.raise_for_status()  # Проверяем, что запрос успешен
        print(f"Успешный запрос к каналу: {channel}")
        feed = feedparser.parse(response.content)

        articles = []
        for entry in reversed(feed.entries):
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published')
            })
        return articles

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе RSS-ленты: {e}")
        raise RSSFetchError(f"Ошибка при запросе RSS-ленты: {e}")


