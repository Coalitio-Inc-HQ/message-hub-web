import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
import aiohttp
from aiohttp import web

# Токен  бота (замените 'YOUR_TELEGRAM_BOT_TOKEN' на реальный токен)
API_TOKEN = '7341102814:AAGS25_CGIrs-xWI0v2qLB4JKwUFBpntFmQ'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Переменная для хранения сообщений пользователей
user_messages = {}
NODE_SERVER_URL = 'http://localhost:3000/message'

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    logging.info(f"Получена команда /start от пользователя {message.from_user.full_name}")
    await message.answer(f"Привет {message.from_user.full_name}!")

# Обработчик обычного сообщения
@dp.message()
async def handle_message(message: types.Message):
    logging.info(f"Получено сообщение от {message.from_user.full_name}: {message.text}")

    message_data = {
        'full_name': message.from_user.full_name,
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'message_id': message.message_id,
        'message_text': message.text,
        'date': message.date.isoformat(),
    }

    logging.info(f"Подготовка данных для отправки на сервер: {message_data}")

    async with aiohttp.ClientSession() as session:
        async with session.post(NODE_SERVER_URL, json=message_data) as resp:
            if resp.status == 200:
                logging.info(f"Сообщение успешно отправлено на сервер: {message_data}")
                await message.reply("Сообщение сохранено и отправлено на сервер!")
            else:
                logging.error(f"Ошибка при отправке сообщения на сервер, статус: {resp.status}")
                await message.reply("Ошибка при отправке сообщения на сервер")

# Обработчик для отправки сообщений из веба в Telegram
async def handle_send_message(request):
    logging.info("Получен запрос на отправку сообщения из веба")
    data = await request.json()
    chat_id = data.get('chatId')
    text = data.get('text')
    logging.info(f"Отправка сообщения в чат {chat_id}: {text}")
    if chat_id and text:
        try:
            await bot.send_message(chat_id, text)
            logging.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return web.Response(status=200, text="Сообщение отправлено")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
            return web.Response(status=500, text=f"Ошибка при отправке сообщения: {e}")
    logging.error("Некорректные данные для отправки сообщения: chat_id или text отсутствуют")
    return web.Response(status=400, text="Ошибка при отправке сообщения")

# Основной процесс бота
async def main():
    app = web.Application()
    app.router.add_post('/send-message', handle_send_message)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    
    logging.info("Сервер запущен на http://localhost:8000")

    try:
        # Запуск диспетчера
        logging.info("Запуск бота...")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
