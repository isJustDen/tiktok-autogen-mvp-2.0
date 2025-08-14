#bot.py
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import BOT_TOKEN
from db import get_today_trends, approve_trend, init_db

BOT_TOKEN = BOT_TOKEN

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# /start — показать тренды
@dp.message(Command("start"))
async def cmd_start(message: Message):
	trends = get_today_trends(limit=10)
	if not trends:
		await message.answer("Сегодня трендов нет(ошибка)")
		return

	for trend in trends:
		trend_id, source, keyword, url, date = trend
		kb = InlineKeyboardMarkup(inline_keyboard=[
			[
			InlineKeyboardButton(text = '✅ Одобрить', callback_data=f"approve_{trend_id}"),
			InlineKeyboardButton(text= "⏭ Пропустить", callback_data='skip'),
			]
		])
		text = f"<b>{keyword}</b>\nИсточник: {source}\n<a href='{url}'>Ссылка</a>"
		await message.answer(text, reply_markup=kb)
# Обработка кнопок
@dp.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_callback(callback: types.CallbackQuery):
	trend_id = int(callback.data.split("_")[1])
	approve_trend(trend_id)
	await callback.answer("Тренд одобрен ✅", show_alert=True)
@dp.callback_query(lambda c: c.data == "skip")
async def skip_callback(callback: types.CallbackQuery):
	await callback.answer('Пропущено ⏭', show_alert=False)

async def main():
	init_db()
	await dp.start_polling(bot)

if __name__ == '__main__':
	asyncio.run(main())

