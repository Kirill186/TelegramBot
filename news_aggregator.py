import requests
from config import NEWS_API_KEY


def get_news_by_category(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    news = []
    for article in data['articles']:
        news.append({
            'title': article['title'],
            'url': article['url']
        })
    return news
