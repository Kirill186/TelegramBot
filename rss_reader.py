import feedparser
import requests
from datetime import datetime
import json


def get_rss_feed(channel):
    try:
        response = requests.get(channel)
        response.raise_for_status()  # Проверяем, что запрос успешен
        feed = feedparser.parse(response.content)

        articles = []
        for entry in reversed(feed.entries):
            published = entry.get('published')
            published = parse_rfc2822_to_iso8601(published)
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': published
            })
        return articles

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе RSS-ленты: {e}")
        return []


def parse_rfc2822_to_iso8601(rfc2822_str):

    # Преобразование строки RFC 2822 во внутренний объект datetime
    parsed_time = datetime.strptime(rfc2822_str, '%a, %d %b %Y %H:%M:%S %Z')

    # Возвращаем время в формате ISO 8601
    return parsed_time.strftime('%Y-%m-%dT%H:%M:%SZ')


# Функция для сохранения времени последней проверки в файл
def save_last_check_time(last_check_time):
    with open('last_check_time.json', 'w') as file:
        json.dump({'last_check_time': last_check_time.isoformat()}, file)

# Функция для загрузки времени последней проверки из файла


def load_last_check_time():
    try:
        with open('last_check_time.json', 'r') as file:
            data = json.load(file)
            return datetime.fromisoformat(data['last_check_time'])
    except (FileNotFoundError, KeyError, ValueError):
        # Если файл не найден возвращаем 0
        return None
