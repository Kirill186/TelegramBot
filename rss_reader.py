import feedparser

def get_rss_feed(url):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'id': entry.link  # Используем ссылку как уникальный ID
        })
    return articles
