#db.py

import datetime
import logging
import re
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import unquote


# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('trends.log', encoding='utf-8'), logging.StreamHandler()])
logger  = logging.getLogger(__name__)


DB_NAME = 'trends.db'

def init_db():
	"""Инициализация базы данных для хранения трендов"""
	try:
		with sqlite3.connect(DB_NAME) as conn:
			conn.execute("""
			CREATE TABLE IF NOT EXISTS trends(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			source TEXT NOT NULL,
			keyword TEXT NOT NULL,
			url TEXT,
			date TEXT NOT NULL,
			UNIQUE(source, keyword, date)
			)
			""")
			conn.execute("""
			CREATE TABLE IF NOT EXISTS approved_trends(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			trend_id INTEGER NOT NULL,
			approved_date TEXT NOT NULL,
			FOREIGN KEY (trend_id) REFERENCES trends(id)
			)
			""")

			logger.info('База данных инициализированна')
	except sqlite3.Error as e:
		logger.error(f"Ошибка при инициализации БД: {e}")


def save_trend(source: str, keyword: str, url: str = None):
	"""Сохранение тренда в базу данных"""
	try:
		with sqlite3.connect(DB_NAME) as conn:
			conn.execute("""
			INSERT OR IGNORE INTO trends(source, keyword, url, date) 
			VALUES (?, ?, ?, ?)
			""", (source, keyword, url, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
			logger.debug(f"Сохранен тренд: {source} - {keyword} - {url}")
	except sqlite3.Error as e:
		logger.error(f"Ошибка при сохранении в БД: {e}")


def clean_text(text: str) -> str:
	"""Очистка текста от спецсимволов и URL-encoding"""
	try:
		decoded = unquote(text)
		cleaned = re.sub(r'[^\w\s#@а-яА-ЯёЁ-]', '', decoded)
		return cleaned.strip().lower()
	except:
		return text.strip().lower()


def is_similar(text1: str, text2: str, threshold: float = 0.6) -> bool:
	"""Проверка схожести строк с пороговым значением"""
	words1 = re.findall(r'\w+', text1)
	words2 = re.findall(r'\w+', text2)
	return SequenceMatcher(None, " ".join(words1), " ".join(words2)).ratio() > threshold

def get_today_trends(limit=10):
	"""Получение(запись) сегодняшних трендов"""
	today =  datetime.now().strftime('%Y-%m-%d')
	with sqlite3.connect(DB_NAME) as conn:
		cur = conn.execute("""
		SELECT id, source, keyword, url, date
		FROM trends
		WHERE date LIKE ?
		ORDER BY date DESC
		limit ?
		""", (f"{today}%", limit))
		return cur.fetchall()

def approve_trend(trend_id: int):
	try:
		with sqlite3.connect(DB_NAME) as conn:
			conn.execute("""
			INSERT INTO approved_trends(trend_id, approved_date)
			VALUES (?, ?)
			""", (trend_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
	except sqlite3.Error as e:
		logger.error(f"Ошибка при одобрении тренда: {e}")
		raise
