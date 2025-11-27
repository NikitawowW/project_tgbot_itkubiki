import asyncio
import logging

from aiogram import Dispatcher

from handlers import router, bot

dp = Dispatcher()
logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())