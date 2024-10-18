import asyncio
import logging
import sys

from decouple import config
from app.handlers.handler_main import router_main
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage

async def main():
    bot = Bot(token=config('BOT_TOKEN'))
    await bot.delete_webhook()
    dp = Dispatcher(storage=RedisStorage.from_url(config('REDIS_URL')))
    dp.include_router(router_main)
    await dp.start_polling(bot, polling_timeout=100)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
        print("Bot start")
    except KeyboardInterrupt:
        print('Bot stop')
    except Exception as e:
        print(e)