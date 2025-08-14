# fetch_trends.py

import io
import logging

import sys
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from config import USER_AGENT
from db import clean_text, is_similar, save_trend

USER_AGENT = USER_AGENT

# Фикс кодировки для Windows
if sys.stdout.encoding != 'UTF-8':
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('trends.log', encoding='utf-8'), logging.StreamHandler()])
logger  = logging.getLogger(__name__)


def fetch_trends24(country: str = 'russia') -> list:
	"""Получение трендов с Trends24.in"""
	logger.info("[*] Получаю тренды с Trends24...")
	url = f"https://trends24.in/{country}/"
	headers = {
		"User-Agent": USER_AGENT,
		"Accept-Language": "ru-Ru,ru;q=0.9"
	}

	try:
		response = requests.get(url, headers=headers, timeout=15)
		response.encoding = 'utf-8'
		soup = BeautifulSoup(response.text, 'html.parser')

		trends = []
		for item in soup.select('.trend-card__list a'):
			trend_text = clean_text(item.text)
			trend_url = item.get('href', "")

			# Форматирование URL
			if trend_url and not trend_url.startswith('http'):
				trend_url = f"https://twitter.com/search?q={trend_url.split('=')[-1]}" if '=' in trend_url else ""

			# Проверка на дубликаты
			if trend_text and not any(is_similar(trend_text, t['text']) for t in trends):
				trends.append({
					'text': trend_text,
					"url": trend_url
				})
				save_trend("Trends24", trend_text, trend_url)
				logger.info(f"[Trends24] {trend_text}")

		return trends[:7] # Возвращаем топ-7 трендов

	except Exception as e:
		logger.error(f"шибка при парсинге Trends24: {str(e)}")
		return []

def fetch_reddit_trends(posts_per_sub: int = 3, max_subs: int = 5) -> list:
	"""Получение трендов с русскоязычных сабреддитов Reddit"""
	logger.info("[*] Получаю тренды с Reddit...")
	russian_subs = [    'Pikabu', 'Epicentr', 'PopLaw', 'Kafka',
    'rusAskReddit', 'tjournal_refugees', 'liberta',
    'MobileOverview', 'RU_games', 'politota']

	headers = {'User-Agent': USER_AGENT,
	           "Accept-Encoding": "gzip"}
	subs_posts = defaultdict(list)

	for sub in russian_subs[:max_subs]:
		try:
			url = f"https://www.reddit.com/r/{sub}/top.json?sort=top&t=day&limit={posts_per_sub*2}"
			response = requests.get(url, headers=headers, timeout=15)
			response.raise_for_status()

			data = response.json()
			for post in data['data']['children']:
				post_data = post['data']
				if (any(ord(c) > 1024 for c in post_data["title"]) and not post_data['over_18']):
					subs_posts[sub].append({
						'title': post_data['title'],
						'url': f"https://reddit.com{post_data['permalink']}",
						'score': post_data['score'],
						'comments': post_data['num_comments']
					})
			logger.info(f"Получено {len(subs_posts[sub])} постов из r/{sub}")

		except Exception as e:
			logger.warning(f"Ошибка при запросе r/{sub}: {str(e)}")

	# Сбор и сортировка постов
	all_posts = []
	for sub, posts in subs_posts.items():
		for post in posts[:posts_per_sub]:
			all_posts.append((sub, post))

	all_posts.sort(key=lambda x: x[1]['score'] + x[1]['comments'], reverse=True)

	# Сохранение в БД
	for sub, post in all_posts:
		save_trend(f"Reddit/{sub}", post['title'], post['url'])

	return all_posts[:15]  # Возвращаем топ-15 постов

def print_results(trends: list, source: str):
	"""Красивый вывод результатов"""
	print(f"\n🔥 Топ трендов ({source}):")
	for i, item in enumerate(trends, 1):
		if source == 'Trends24':
			print(f"{i}. {item['text'].capitalize()}")
			print(f"   🔗 {item['url']}\n")
		else:
			sub, post = item
			print(f"{i}. [r/{sub}] {post['title']}")
			print(f"   👍 {post['score']} | 💬 {post['comments']}")
			print(f"   🔗 {post['url']}\n")










