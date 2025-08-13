import os
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import settings

from faststream.rabbit import RabbitBroker


bot = Bot(token=settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
        )
storage = RedisStorage(redis)
dp = Dispatcher(storage=storage)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "scrapers")

broker = RabbitBroker(url=f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")


@broker.subscriber("scrapers")
async def handle_orders_and_send_message(data: str):
    await bot.send_message(
        chat_id=settings.chat_id,
        text=data,
    )


async def main() -> None:
    async with broker:
        await broker.start()
        logging.info("Брокер стартовал")
        await dp.start_polling(bot)
    logging.info("Все закончилось...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
