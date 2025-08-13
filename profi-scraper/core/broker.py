from faststream.rabbit import RabbitBroker
from core.config import settings


broker = RabbitBroker(
    url=f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:{settings.rabbitmq_port}/",
)


async def send_message(message: str):
    async with broker:
        await broker.publish(message, settings.rabbitmq_queue)


async def send_messages(messages: list[str]) -> None:
    for message in messages:
        await send_message(message)
