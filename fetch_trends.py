# fetch_trends.py
import sqlite3
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DB_NAME = 'trends.db'

def save_trend(keyword):
	"""Сохраняем тренды в БД"""
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute("""
	CREATE TABLE IF NOT EXISTS trends(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	keyword TEXT,
	date TEXT,
	)""")
	cur.execute("INSERT INTO trends (keyword, date) VALUES (?, ?)",
	            (keyword, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
	conn.commit()
	conn.close()

def fetch_google_trends():
	url = "https://trends.google.com/trending?geo=RU"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	# Для MVP берём заглушку, позже заменим на API
	fake_trends = ['Тренд №1', "Тренд №2"]
	for trend in fake_trends:
		save_trend(trend)
		print(f"[+] Сохранён тренд: {trend}")


if __name__ == '__main__':
	fetch_google_trends()
