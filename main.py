#main.py
import logging

from db import init_db
from fetch_trends import fetch_trends24, fetch_reddit_trends, print_results


# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('trends.log', encoding='utf-8'), logging.StreamHandler()])
logger  = logging.getLogger(__name__)


if __name__ == '__main__':
	init_db()

	# Сбор трендов
	trends24_data = fetch_trends24()
	reddit_data = fetch_reddit_trends()

	# Вывод результатов
	print_results(trends24_data, 'Trends24')
	print_results(reddit_data, 'Reddit')

	logger.info("Сбор трендов завершён")